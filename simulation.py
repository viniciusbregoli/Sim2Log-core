"""
Módulo de simulação de logs usando SimPy.

Gera logs sintéticos baseados em modelos de processo extraídos.
"""

import csv
import math
import random
import re
import time
from copy import copy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

import simpy
from pm4py.objects.petri_net import semantics
from pm4py.util import xes_constants

from models import ProcessModel, SimulationConfig, SimulationResult


class ActivityExecutor:
    """
    Gerencia execução de atividades na simulação.
    
    Gera dinamicamente métodos para cada atividade baseado nas durações.
    """
    
    def __init__(self, env: simpy.Environment, activity_durations: Dict[str, float]):
        """
        Args:
            env: Ambiente SimPy
            activity_durations: Dicionário {atividade: duração_segundos}
        """
        self.env = env
        self._durations = activity_durations
    
    def execute(self, activity_name: str):
        """
        Executa uma atividade (gerador SimPy).
        
        Args:
            activity_name: Nome da atividade
            
        Yields:
            Timeout do SimPy
        """
        # Normaliza nome (remove caracteres especiais)
        normalized_name = re.sub(r"[^A-Za-z0-9]", "", activity_name)
        
        # Obtém duração
        duration = self._durations.get(activity_name, 0)
        duration = max(0, math.ceil(duration))  # Garante não-negativo e inteiro
        
        yield self.env.timeout(duration)


class LogSimulator:
    """
    Simulador de logs usando SimPy e Redes de Petri.
    
    Example:
        >>> config = SimulationConfig(num_cases=100)
        >>> simulator = LogSimulator(config)
        >>> result = simulator.simulate(process_model, output_dir="output")
        >>> print(result.num_events_generated)
        542
    """
    
    def __init__(self, config: SimulationConfig, verbose: bool = True):
        """
        Args:
            config: Configuração da simulação
            verbose: Se True, imprime progresso
        """
        self.config = config
        self.verbose = verbose
        self._events: list = []
    
    def simulate(
        self,
        process_model: ProcessModel,
        output_dir: Path | str = ".",
        output_prefix: str = "simulated-logs"
    ) -> SimulationResult:
        """
        Executa simulação e gera logs sintéticos.
        
        Args:
            process_model: Modelo de processo minerado
            output_dir: Diretório para salvar os logs
            output_prefix: Prefixo dos arquivos gerados
            
        Returns:
            SimulationResult com informações da simulação
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        csv_path = output_dir / f"{output_prefix}.csv"
        xes_path = output_dir / f"{output_prefix}.xes"
        
        self._log(f"Iniciando simulação de {self.config.num_cases} casos...")
        
        start_time = time.time()
        
        # Prepara durações de atividades
        activity_durations = self._prepare_activity_durations(process_model)
        
        # Determina taxa de chegada
        arrival_rate = self.config.arrival_rate or process_model.arrival_rate
        self._log(f"Taxa de chegada: {arrival_rate:.2f} min/caso")
        
        # Executa simulação
        random.seed(self.config.random_seed)
        self._events = []
        
        env = simpy.Environment()
        env.process(self._setup(
            env,
            process_model,
            activity_durations,
            arrival_rate
        ))
        env.run()
        
        simulation_time = time.time() - start_time
        
        # Salva em CSV
        self._log(f"Salvando {len(self._events)} eventos em CSV...")
        self._save_csv(csv_path)
        
        # Converte para XES
        self._log("Convertendo para XES...")
        self._convert_csv_to_xes(csv_path, xes_path)
        
        num_cases = len(set(event[0] for event in self._events if event[1] != "case end"))
        num_events = len([e for e in self._events if e[1] != "case end"])
        
        self._log(f"✓ Simulação concluída em {simulation_time:.2f}s")
        self._log(f"  Casos gerados: {num_cases}")
        self._log(f"  Eventos gerados: {num_events}")
        
        return SimulationResult(
            csv_path=csv_path,
            xes_path=xes_path,
            num_cases_generated=num_cases,
            num_events_generated=num_events,
            simulation_time=simulation_time
        )
    
    def _prepare_activity_durations(self, model: ProcessModel) -> Dict[str, float]:
        """Prepara dicionário de durações de atividades."""
        durations = {}
        
        for activity_name, stats in model.activities.items():
            # Usa duração customizada se fornecida, senão usa a minerada
            if self.config.activity_durations and activity_name in self.config.activity_durations:
                durations[activity_name] = self.config.activity_durations[activity_name]
            else:
                durations[activity_name] = stats.mean_duration
        
        return durations
    
    def _setup(
        self,
        env: simpy.Environment,
        model: ProcessModel,
        activity_durations: Dict[str, float],
        arrival_rate: float
    ):
        """
        Configura e inicia geração de casos.
        
        Gerador SimPy que cria casos com intervalos de chegada.
        """
        executor = ActivityExecutor(env, activity_durations)
        
        for case_id in range(1, self.config.num_cases + 1):
            # Aguarda próxima chegada
            yield env.timeout(arrival_rate)
            
            # Inicia simulação do caso
            env.process(self._simulate_case(
                env,
                f"Case {case_id}",
                executor,
                model
            ))
    
    def _simulate_case(
        self,
        env: simpy.Environment,
        case_id: str,
        executor: ActivityExecutor,
        model: ProcessModel
    ):
        """
        Simula um caso individual seguindo a semântica da Rede de Petri.
        
        Args:
            env: Ambiente SimPy
            case_id: ID do caso
            executor: Executor de atividades
            model: Modelo de processo
        """
        marking = copy(model.initial_marking)
        trace_length = 0
        
        while True:
            # Verifica se chegou ao fim
            enabled_transitions = list(semantics.enabled_transitions(
                model.petri_net,
                marking
            ))
            
            if not enabled_transitions:
                break
            
            # Escolhe aleatoriamente uma transição habilitada
            random.shuffle(enabled_transitions)
            transition = enabled_transitions[0]
            
            # Executa atividade se não for transição silenciosa
            if transition.label is not None:
                timestamp = datetime.now() + timedelta(seconds=env.now)
                
                # Registra evento
                self._events.append([case_id, transition.label, timestamp])
                
                # Executa atividade (pausa simulação)
                yield env.process(executor.execute(transition.label))
                
                trace_length += 1
            
            # Atualiza marcação da rede
            marking = semantics.execute(transition, model.petri_net, marking)
            
            # Limite de segurança
            if trace_length > self.config.max_trace_length:
                self._log(f"AVISO: {case_id} excedeu limite de {self.config.max_trace_length} eventos")
                break
        
        # Marca fim do caso
        self._events.append([
            case_id,
            "case end",
            datetime.now() + timedelta(seconds=env.now)
        ])
    
    def _save_csv(self, path: Path):
        """Salva eventos em CSV."""
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['case_id', 'activity', 'time:timestamp'])
            
            for event in self._events:
                if event[1] != "case end":  # Remove marcadores internos
                    writer.writerow(event)
    
    def _convert_csv_to_xes(self, csv_path: Path, xes_path: Path):
        """Converte CSV para formato XES."""
        import pandas as pd
        import pm4py
        from pm4py.objects.conversion.log import converter as log_converter
        
        # Lê CSV
        df = pd.read_csv(csv_path, sep=',')
        
        # Formata como event log
        event_log = pm4py.format_dataframe(
            df,
            case_id='case_id',
            activity_key='activity',
            timestamp_key='time:timestamp'
        )
        
        # Converte para XES
        log = log_converter.apply(event_log)
        pm4py.write_xes(log, str(xes_path))
        
        # Adiciona classificador (necessário para algumas ferramentas)
        with open(xes_path, "r", encoding='utf-8') as f:
            contents = f.readlines()
        
        # Insere classificador após a linha 4 (após <log>)
        if len(contents) > 5:
            contents.insert(5, '  <classifier name="Activity" keys="concept:name"/>\n')
        
        with open(xes_path, "w", encoding='utf-8') as f:
            f.write("".join(contents))
    
    def _log(self, message: str):
        """Imprime mensagem se verbose ativado."""
        if self.verbose:
            print(f"[LogSimulator] {message}")

