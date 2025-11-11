"""
Módulo de mineração de processos.

Extrai modelo de processo, estatísticas e parâmetros de logs XES.
"""

import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import warnings
warnings.filterwarnings('ignore')

# Workaround para bug no pm4py 2.2.22 com Python 3.11
import sys
if 'pm4py' not in sys.modules:
    import deprecation
    original_deprecated = deprecation.deprecated
    def patched_deprecated(*args, **kwargs):
        if len(args) >= 3 and isinstance(args[2], str) and 'please use' in args[2]:
            args = list(args)
            args[2] = ''  # Remove mensagem problemática
        return original_deprecated(*args, **kwargs)
    deprecation.deprecated = patched_deprecated

import pandas as pd
import scipy.stats
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer

from models import ActivityStatistics, ProcessModel
from log_analyzer import LogAnalyzer, LogProfile


class DistributionFitter:
    """Identifica a melhor distribuição estatística para um conjunto de dados."""
    
    DISTRIBUTIONS = ['norm', 'lognorm', 'expon']
    
    @classmethod
    def fit(cls, data: List[float]) -> Tuple[str, float, Tuple]:
        """
        Identifica a melhor distribuição usando teste de Kolmogorov-Smirnov.
        
        Args:
            data: Lista de valores
            
        Returns:
            Tupla (nome_distribuicao, p_value, parametros)
        """
        if not data or len(data) < 2:
            raise ValueError("Dados insuficientes para ajuste de distribuição")
        
        results = []
        params_dict = {}
        
        for dist_name in cls.DISTRIBUTIONS:
            try:
                dist = getattr(scipy.stats, dist_name)
                params = dist.fit(data)
                params_dict[dist_name] = params
                
                # Teste de Kolmogorov-Smirnov
                _, p_value = scipy.stats.kstest(data, dist_name, args=params)
                results.append((dist_name, p_value))
            except Exception:
                continue
        
        if not results:
            # Fallback para distribuição normal
            return 'norm', 0.0, (statistics.mean(data), statistics.stdev(data))
        
        # Seleciona distribuição com maior p-value
        best_dist, best_p = max(results, key=lambda x: x[1])
        return best_dist, best_p, params_dict[best_dist]


class ProcessMiner:
    """
    Minerador de processos que extrai modelo e estatísticas de logs XES.
    
    Example:
        >>> miner = ProcessMiner()
        >>> model = miner.mine_process("event_log.xes", variant_filter=0.8)
        >>> print(model.arrival_rate)
        5.2
    """
    
    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Se True, imprime informações durante o processamento
        """
        self.verbose = verbose
    
    def mine_process(
        self,
        log_path: Path | str,
        variant_filter: float = 0.8,
        save_model_image: Optional[Path] = None,
        auto_detect: bool = True
    ) -> ProcessModel:
        """
        Minera processo completo de um log XES.
        
        Este método é GENÉRICO e funciona com qualquer log XES, independente
        do domínio (hospitalar, financeiro, varejo, manufatura, etc).
        
        Args:
            log_path: Caminho do arquivo XES
            variant_filter: Percentual de variantes a manter (0.0 a 1.0)
            save_model_image: Se fornecido, salva imagem da rede de Petri
            auto_detect: Se True, detecta automaticamente características do log
            
        Returns:
            ProcessModel com todas as informações extraídas
        """
        log_path = Path(log_path)
        
        if not log_path.exists():
            raise FileNotFoundError(f"Log não encontrado: {log_path}")
        
        # Análise automática do log
        log_profile = None
        if auto_detect:
            self._log("Analisando características do log...")
            analyzer = LogAnalyzer(verbose=self.verbose)
            log_profile = analyzer.analyze(log_path)
            
            # Valida compatibilidade
            is_compatible, warnings = analyzer.validate_compatibility(log_profile)
            if not is_compatible:
                raise ValueError(
                    f"Log incompatível com Sim2Log:\n" + "\n".join(warnings)
                )
            
            if warnings:
                for warning in warnings:
                    self._log(f"  {warning}")
        
        self._log("Carregando log XES...")
        original_log = xes_importer.apply(str(log_path))
        num_cases_original = len(original_log)
        
        self._log(f"Log carregado: {num_cases_original} casos")
        
        # Filtra variantes
        self._log(f"Filtrando variantes ({variant_filter*100:.0f}%)...")
        from pm4py.algo.filtering.log.variants import variants_filter
        filtered_log = variants_filter.filter_log_variants_percentage(
            original_log, 
            percentage=variant_filter
        )
        num_variants = len(filtered_log)
        
        self._log(f"Após filtragem: {num_variants} casos")
        
        # Descobre rede de Petri
        self._log("Descobrindo modelo de processo (Inductive Miner)...")
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        net, im, fm = inductive_miner.apply(filtered_log)

        # Descobre Process Tree
        self._log("Descobrindo Process Tree...")
        process_tree = pm4py.discover_process_tree_inductive(
            filtered_log,
            noise_threshold=1 - variant_filter  # Usa threshold baseado no filtro
        )

        # Salva visualização se solicitado
        if save_model_image:
            self._log(f"Salvando imagem do modelo em {save_model_image}...")
            save_model_image.parent.mkdir(parents=True, exist_ok=True)
            from pm4py.visualization.petri_net import visualizer as pn_visualizer

            # Gera visualização da Rede de Petri
            gviz = pn_visualizer.apply(net, im, fm)
            pn_visualizer.save(gviz, str(save_model_image))

            # Gera visualização da Process Tree
            tree_image_path = save_model_image.parent / f"{save_model_image.stem}_tree{save_model_image.suffix}"
            self._log(f"Salvando Process Tree em {tree_image_path}...")
            pm4py.save_vis_process_tree(process_tree, str(tree_image_path))
        
        # Avalia qualidade do modelo
        self._log("Avaliando qualidade do modelo...")
        quality = self._evaluate_model(filtered_log, net, im, fm)
        
        # Extrai estatísticas temporais
        self._log("Extraindo estatísticas de atividades...")
        activities = self._extract_activity_statistics(filtered_log)
        
        # Extrai métricas gerais
        self._log("Calculando métricas gerais...")
        arrival_rate = self._get_arrival_rate(original_log)
        dispersion_rate = self._get_dispersion_rate(original_log)
        median_duration = self._get_median_case_duration(original_log)
        
        # Extrai recursos
        resources = self._extract_resources(filtered_log)
        
        model = ProcessModel(
            petri_net=net,
            initial_marking=im,
            final_marking=fm,
            activities=activities,
            arrival_rate=arrival_rate,
            dispersion_rate=dispersion_rate,
            median_case_duration=median_duration,
            num_cases=num_cases_original,
            num_variants=num_variants,
            quality_metrics=quality,
            resources=resources,
            log_profile=log_profile,
            process_tree=process_tree
        )
        
        self._log("Mineração concluída com sucesso.")
        self._log(f"Modelo extraído com {len(activities)} atividades e fitness de {quality.get('fitness', 0):.3f}")
        return model
    
    def _evaluate_model(self, log, net, im, fm) -> Dict[str, float]:
        """Avalia qualidade do modelo descoberto."""
        try:
            from pm4py.algo.evaluation.replay_fitness import evaluator as replay_fitness_evaluator
            fitness_result = replay_fitness_evaluator.apply(
                log, net, im, fm,
                variant=replay_fitness_evaluator.Variants.ALIGNMENT_BASED
            )
            fitness = round(fitness_result.get('averageFitness', 0.0), 3)
        except Exception as e:
            self._log(f"AVISO: Não foi possível calcular fitness: {e}")
            fitness = 0.0
        
        try:
            from pm4py.algo.evaluation.precision import evaluator as precision_evaluator
            precision = round(precision_evaluator.apply(
                log, net, im, fm,
                variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN
            ), 3)
        except Exception as e:
            self._log(f"AVISO: Não foi possível calcular precision: {e}")
            precision = 0.0
        
        try:
            from pm4py.algo.evaluation.simplicity import evaluator as simplicity_evaluator
            simplicity = round(simplicity_evaluator.apply(net), 3)
        except Exception as e:
            self._log(f"AVISO: Não foi possível calcular simplicity: {e}")
            simplicity = 0.0
        
        return {
            'fitness': fitness,
            'precision': precision,
            'simplicity': simplicity
        }
    
    def _extract_activity_statistics(self, log) -> Dict[str, ActivityStatistics]:
        """Extrai estatísticas temporais de cada atividade."""
        durations_by_activity = {}
        
        for trace in log:
            length = len(trace)
            for index, event in enumerate(trace):
                if "concept:name" not in event:
                    continue
                
                activity = event["concept:name"]
                
                # Calcula duração
                if index < (length - 1):
                    next_event = trace[index + 1]
                    
                    if "time:complete" in event:
                        duration = (event["time:complete"] - event["time:timestamp"]).total_seconds()
                    elif "time:timestamp" in event and "time:timestamp" in next_event:
                        duration = (next_event["time:timestamp"] - event["time:timestamp"]).total_seconds()
                    else:
                        continue
                else:
                    # Última atividade: usa média das anteriores
                    if activity in durations_by_activity:
                        duration = statistics.mean(durations_by_activity[activity])
                    else:
                        continue
                
                if activity not in durations_by_activity:
                    durations_by_activity[activity] = []
                durations_by_activity[activity].append(duration)
        
        # Limpa dados usando pandas
        df = pd.DataFrame.from_dict(durations_by_activity, orient='index').transpose()
        df.dropna(inplace=True)
        durations_by_activity = df.to_dict('list')
        
        # Ajusta distribuições
        activities = {}
        for activity, durations in durations_by_activity.items():
            if not durations:
                continue
            
            mean_duration = statistics.mean(durations)
            
            try:
                dist_name, p_value, params = DistributionFitter.fit(durations)
            except ValueError:
                # Dados insuficientes, usa apenas a média
                dist_name = 'constant'
                p_value = 1.0
                params = (mean_duration,)
            
            activities[activity] = ActivityStatistics(
                name=activity,
                mean_duration=mean_duration,
                durations=durations,
                distribution_name=dist_name,
                distribution_params=params,
                p_value=p_value
            )
        
        return activities
    
    def _get_arrival_rate(self, log) -> float:
        """Calcula taxa de chegada de casos em minutos."""
        try:
            from pm4py.statistics.traces.generic.log import case_arrival
            case_arrival_ratio = case_arrival.get_case_arrival_avg(
                log, 
                parameters={case_arrival.Parameters.TIMESTAMP_KEY: "time:timestamp"}
            )
            return round(case_arrival_ratio / 60, 2)
        except Exception:
            # Fallback: calcula manualmente
            if not log:
                return 1.0
            timestamps = []
            for trace in log:
                if trace and "time:timestamp" in trace[0]:
                    timestamps.append(trace[0]["time:timestamp"])
            if len(timestamps) < 2:
                return 1.0
            timestamps.sort()
            total_time = (timestamps[-1] - timestamps[0]).total_seconds()
            return round((total_time / len(timestamps)) / 60, 2)
    
    def _get_dispersion_rate(self, log) -> float:
        """Calcula taxa de dispersão (saída) de casos em minutos."""
        try:
            from pm4py.statistics.traces.generic.log import case_arrival
            case_dispersion_ratio = case_arrival.get_case_dispersion_avg(
                log,
                parameters={case_arrival.Parameters.TIMESTAMP_KEY: "time:timestamp"}
            )
            return round(case_dispersion_ratio / 60, 2)
        except Exception:
            return self._get_arrival_rate(log)  # Usa mesma taxa como fallback
    
    def _get_median_case_duration(self, log) -> float:
        """Calcula duração mediana dos casos."""
        try:
            from pm4py.statistics.traces.generic.log import case_statistics
            return case_statistics.get_median_caseduration(
                log,
                parameters={case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"}
            )
        except Exception:
            # Fallback: calcula manualmente
            durations = []
            for trace in log:
                if len(trace) >= 2:
                    start = trace[0]["time:timestamp"]
                    end = trace[-1]["time:timestamp"]
                    durations.append((end - start).total_seconds())
            return statistics.median(durations) if durations else 0.0
    
    def _extract_resources(self, log) -> Dict[str, List[str]]:
        """Extrai mapeamento de recursos por atividade."""
        try:
            from pm4py.algo.filtering.log.attributes import attributes_filter
            activities = attributes_filter.get_attribute_values(log, "concept:name")
            resources_by_activity = {}
            
            for activity in activities:
                filtered_log = attributes_filter.apply_events(
                    log, 
                    activity,
                    parameters={
                        attributes_filter.Parameters.ATTRIBUTE_KEY: "concept:name",
                        attributes_filter.Parameters.POSITIVE: True
                    }
                )
                resources = attributes_filter.get_attribute_values(filtered_log, "org:resource")
                resources_by_activity[activity] = list(resources.keys())
            
            return resources_by_activity
        except Exception:
            # Fallback: extração manual simples
            resources_by_activity = {}
            for trace in log:
                for event in trace:
                    if "concept:name" in event:
                        activity = event["concept:name"]
                        if activity not in resources_by_activity:
                            resources_by_activity[activity] = []
                        if "org:resource" in event:
                            resource = event["org:resource"]
                            if resource not in resources_by_activity[activity]:
                                resources_by_activity[activity].append(resource)
            return resources_by_activity
    
    def _log(self, message: str):
        """Imprime mensagem se verbose ativado."""
        if self.verbose:
            print(f"[ProcessMiner] {message}")

