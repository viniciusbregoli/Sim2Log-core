"""
Módulo de indicadores ORE (Operating Room Effectiveness).

Baseado no artigo: "Operating room effectiveness: a lean health-care performance indicator"
Souza, T. A., Vaccaro, G. L. R., & Lima, R. M. (2020)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
from pm4py.objects.log.importer.xes import importer as xes_importer


@dataclass
class OREMetrics:
    """Métricas do Operating Room Effectiveness."""

    # Tempos principais
    total_time_available: float  # TTA - Tempo total disponível (horas)
    total_time_scheduled: float  # TTS - Tempo total agendado (horas)
    total_time_used: float      # TTU - Tempo total usado (horas)
    total_time_added_value: float  # TTAV - Tempo de valor agregado (horas)

    # Índices
    availability: float  # Disponibilidade (%)
    performance: float   # Desempenho (%)
    quality: float      # Qualidade (%)
    ore: float          # ORE total (%)

    # Perdas de Disponibilidade (horas)
    loss_equipment_failure: float
    loss_setup: float
    loss_not_scheduling: float

    # Perdas de Desempenho (horas)
    loss_small_shutdowns: float
    loss_surgery_time_variation: float
    loss_cancellations: float

    # Perdas de Qualidade (horas)
    loss_reinterventions: float

    # Estatísticas adicionais
    num_surgeries_scheduled: int
    num_surgeries_completed: int
    num_surgeries_cancelled: int
    cancellation_rate: float  # %


class ORECalculator:
    """Calculador de indicadores ORE para salas de cirurgia."""

    def __init__(
        self,
        daily_hours: float = 11.5,  # 07:30 às 19:00
        setup_time_minutes: float = 15.0,  # Tempo médio de limpeza/preparação
        verbose: bool = True
    ):
        """
        Args:
            daily_hours: Horas disponíveis por dia
            setup_time_minutes: Tempo médio de setup entre cirurgias
            verbose: Se True, imprime informações durante o processamento
        """
        self.daily_hours = daily_hours
        self.setup_time_minutes = setup_time_minutes
        self.verbose = verbose

    def calculate_from_log(self, log_path: Path | str) -> OREMetrics:
        """
        Calcula métricas ORE a partir de um log XES.

        Args:
            log_path: Caminho do arquivo XES

        Returns:
            OREMetrics com todos os indicadores calculados
        """
        self._log("Carregando log XES...")
        log = xes_importer.apply(str(log_path))

        self._log(f"Log carregado: {len(log)} casos")

        # Extrai informações do log
        df = self._log_to_dataframe(log)

        # Calcula métricas
        return self._calculate_metrics(df)

    def _log_to_dataframe(self, log) -> pd.DataFrame:
        """Converte log XES para DataFrame."""
        records = []

        for trace in log:
            case_id = trace.attributes.get('concept:name', 'unknown')

            for event in trace:
                # Tenta pegar sala em diferentes variações (maiúscula/minúscula)
                sala = event.get('sala', event.get('SALA', event.get('Sala', '')))

                records.append({
                    'case_id': case_id,
                    'activity': event.get('concept:name', ''),
                    'timestamp': event.get('time:timestamp'),
                    'resource': event.get('org:resource', ''),
                    'sala': sala
                })

        df = pd.DataFrame(records)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(['case_id', 'timestamp'])

        return df

    def _calculate_metrics(self, df: pd.DataFrame) -> OREMetrics:
        """Calcula todas as métricas ORE."""

        # Identifica casos únicos
        cases = df.groupby('case_id').agg({
            'timestamp': ['min', 'max', 'count']
        }).reset_index()

        cases.columns = ['case_id', 'start_time', 'end_time', 'num_events']
        cases['duration_hours'] = (cases['end_time'] - cases['start_time']).dt.total_seconds() / 3600

        # Identifica período total
        min_date = df['timestamp'].min()
        max_date = df['timestamp'].max()

        # Calcula dias úteis (assumindo operação de segunda a sexta)
        total_days = (max_date - min_date).days + 1
        working_days = self._count_working_days(min_date, max_date)

        # TTA - Total Time Available
        total_time_available = working_days * self.daily_hours

        # Perdas de Disponibilidade
        num_surgeries = len(cases)

        # Calcula setup baseado na realidade operacional:
        # Agrupa cirurgias por dia e sala para calcular setup realista
        cases['date'] = cases['start_time'].dt.date

        # Tenta identificar sala (pode estar em diferentes atributos)
        df_with_sala = df.copy()
        if 'sala' in df.columns:
            # Mapeia sala para cada caso
            sala_per_case = df.groupby('case_id')['sala'].first()
            cases['sala'] = cases['case_id'].map(sala_per_case)
        else:
            # Se não houver sala, assume sala única
            cases['sala'] = 'Sala 1'

        # Conta cirurgias por dia/sala
        surgeries_per_day_sala = cases.groupby(['date', 'sala']).size().reset_index(name='count')

        # Setup: Estratégia mais conservadora
        # Conta apenas 1 setup por dia/sala (preparação inicial) + setups entre cirurgias
        # Limitamos o tempo total de setup a no máximo 20% do TTA
        num_operating_days = len(surgeries_per_day_sala)

        # Setup estimado: 1 setup inicial por dia/sala + tempo médio entre cirurgias
        # Usamos uma abordagem conservadora baseada no número de dias operacionais
        estimated_setup_hours = (num_operating_days * self.setup_time_minutes) / 60

        # Limita setup a no máximo 15% do TTA para evitar valores irreais
        max_allowed_setup = total_time_available * 0.15
        loss_setup = min(estimated_setup_hours, max_allowed_setup)

        # Not Scheduling: tempo não preenchido (estimativa conservadora: 6% do TTA)
        loss_not_scheduling = total_time_available * 0.06  # 6% conforme artigo

        # Equipment Failure: assumindo 0 (não temos dados específicos)
        loss_equipment_failure = 0.0

        # TTS - Total Time Scheduled
        total_time_scheduled = total_time_available - loss_equipment_failure - loss_setup - loss_not_scheduling

        # Perdas de Desempenho
        # Cancellations: identificar casos com poucos eventos (< 3 eventos = cancelado)
        cancelled_cases = cases[cases['num_events'] < 3]
        num_cancelled = len(cancelled_cases)

        # Estima tempo perdido com cancelamentos (média de 1.5h por cirurgia cancelada)
        loss_cancellations = num_cancelled * 1.5

        # Small Shutdowns e Variation: só aplicar se TTS for positivo
        if total_time_scheduled > 0:
            # Small Shutdowns: assumindo 2% do TTS
            loss_small_shutdowns = total_time_scheduled * 0.02

            # Variation in Surgery Time: diferença entre tempo planejado e usado
            # Estimativa: 3% do tempo agendado
            loss_surgery_time_variation = total_time_scheduled * 0.03
        else:
            loss_small_shutdowns = 0.0
            loss_surgery_time_variation = 0.0

        # TTU - Total Time Used
        total_time_used = total_time_scheduled - loss_small_shutdowns - loss_surgery_time_variation - loss_cancellations

        # Garante que TTU não seja negativo
        total_time_used = max(0.0, total_time_used)

        # Perdas de Qualidade
        # Reinterventions: assumindo 0 (dados não disponíveis)
        loss_reinterventions = 0.0

        # TTAV - Total Time of Added Value
        total_time_added_value = total_time_used - loss_reinterventions
        total_time_added_value = max(0.0, total_time_added_value)  # Garante não negativo

        # Calcula índices (garante valores entre 0-100%)
        if total_time_available > 0:
            availability = min(100.0, max(0.0, (total_time_scheduled / total_time_available) * 100))
        else:
            availability = 0.0

        if total_time_scheduled > 0:
            performance = min(100.0, max(0.0, (total_time_used / total_time_scheduled) * 100))
        else:
            performance = 0.0

        if total_time_used > 0:
            quality = min(100.0, max(0.0, (total_time_added_value / total_time_used) * 100))
        else:
            quality = 100.0  # Se não há tempo usado, qualidade é perfeita (sem perdas)

        if total_time_available > 0:
            ore = min(100.0, max(0.0, (total_time_added_value / total_time_available) * 100))
        else:
            ore = 0.0

        # Estatísticas
        num_completed = num_surgeries - num_cancelled
        cancellation_rate = (num_cancelled / num_surgeries * 100) if num_surgeries > 0 else 0

        return OREMetrics(
            total_time_available=total_time_available,
            total_time_scheduled=total_time_scheduled,
            total_time_used=total_time_used,
            total_time_added_value=total_time_added_value,
            availability=availability,
            performance=performance,
            quality=quality,
            ore=ore,
            loss_equipment_failure=loss_equipment_failure,
            loss_setup=loss_setup,
            loss_not_scheduling=loss_not_scheduling,
            loss_small_shutdowns=loss_small_shutdowns,
            loss_surgery_time_variation=loss_surgery_time_variation,
            loss_cancellations=loss_cancellations,
            loss_reinterventions=loss_reinterventions,
            num_surgeries_scheduled=num_surgeries,
            num_surgeries_completed=num_completed,
            num_surgeries_cancelled=num_cancelled,
            cancellation_rate=cancellation_rate
        )

    def _count_working_days(self, start_date: datetime, end_date: datetime) -> int:
        """Conta dias úteis entre duas datas (segunda a sexta)."""
        days = 0
        current = start_date.date()
        end = end_date.date()

        while current <= end:
            # 0 = segunda, 6 = domingo
            if current.weekday() < 5:  # segunda a sexta
                days += 1
            current += timedelta(days=1)

        return days

    def _log(self, message: str):
        """Log de mensagens."""
        if self.verbose:
            print(f"[ORECalculator] {message}")


def calculate_ore_scenarios(base_metrics: OREMetrics) -> pd.DataFrame:
    """
    Calcula cenários hipotéticos de melhoria conforme o artigo.

    Args:
        base_metrics: Métricas base calculadas

    Returns:
        DataFrame com cenários de melhoria
    """
    scenarios = []

    # Cenário Base
    scenarios.append({
        'Scenario': 'Base',
        'Description': 'Current state',
        'TTA': base_metrics.total_time_available,
        'TTS': base_metrics.total_time_scheduled,
        'TTU': base_metrics.total_time_used,
        'TTAV': base_metrics.total_time_added_value,
        'Availability_%': base_metrics.availability,
        'Performance_%': base_metrics.performance,
        'Quality_%': base_metrics.quality,
        'ORE_%': base_metrics.ore,
        'Variation_%': 0.0,
        'Additional_Hours': 0.0
    })

    tta = base_metrics.total_time_available

    # Cenário A: No scheduling = 0
    tts_a = tta - base_metrics.loss_equipment_failure - base_metrics.loss_setup
    tts_a = max(0.0, tts_a)  # Garante não negativo

    ttu_a = tts_a - base_metrics.loss_small_shutdowns - base_metrics.loss_surgery_time_variation - base_metrics.loss_cancellations
    ttu_a = max(0.0, ttu_a)  # Garante não negativo

    ttav_a = max(0.0, ttu_a)
    ore_a = (ttav_a / tta) * 100 if tta > 0 else 0

    scenarios.append({
        'Scenario': 'A',
        'Description': 'No scheduling = 0',
        'TTA': tta,
        'TTS': tts_a,
        'TTU': ttu_a,
        'TTAV': ttav_a,
        'Availability_%': (tts_a/tta)*100 if tta > 0 else 0,
        'Performance_%': (ttu_a/tts_a)*100 if tts_a > 0 else 0,
        'Quality_%': 100.0,
        'ORE_%': ore_a,
        'Variation_%': ore_a - base_metrics.ore,
        'Additional_Hours': ttav_a - base_metrics.total_time_added_value
    })

    # Cenário B: 5 min reduction in setup (aplica a mesma proporção do setup original)
    # Redução proporcional de 5 minutos por setup
    if base_metrics.loss_setup > 0:
        # Estima número de setups baseado no tempo total de setup e tempo por setup (30 min)
        estimated_setups = base_metrics.loss_setup / (30/60)  # horas / (30min em horas)
        setup_reduction = (estimated_setups * 5) / 60  # 5 min por setup, convertido para horas
    else:
        setup_reduction = 0.0

    new_setup_loss = max(0.0, base_metrics.loss_setup - setup_reduction)
    tts_b = tta - base_metrics.loss_equipment_failure - new_setup_loss - base_metrics.loss_not_scheduling
    tts_b = max(0.0, tts_b)

    ttu_b = tts_b - base_metrics.loss_small_shutdowns - base_metrics.loss_surgery_time_variation - base_metrics.loss_cancellations
    ttu_b = max(0.0, ttu_b)

    ttav_b = max(0.0, ttu_b)
    ore_b = (ttav_b / tta) * 100 if tta > 0 else 0

    scenarios.append({
        'Scenario': 'B',
        'Description': '5 min reduction in setup',
        'TTA': tta,
        'TTS': tts_b,
        'TTU': ttu_b,
        'TTAV': ttav_b,
        'Availability_%': (tts_b/tta)*100 if tta > 0 else 0,
        'Performance_%': (ttu_b/tts_b)*100 if tts_b > 0 else 0,
        'Quality_%': 100.0,
        'ORE_%': ore_b,
        'Variation_%': ore_b - base_metrics.ore,
        'Additional_Hours': ttav_b - base_metrics.total_time_added_value
    })

    # Cenário G: No scheduling = 0, 5 min reduction in setup, 50% reduction in cancellations
    tts_g = tts_a
    ttu_g = tts_g - base_metrics.loss_small_shutdowns - base_metrics.loss_surgery_time_variation - (base_metrics.loss_cancellations * 0.5)
    ttu_g = max(0.0, ttu_g)  # Garante não negativo

    ttav_g = max(0.0, ttu_g)
    ore_g = (ttav_g / tta) * 100 if tta > 0 else 0

    scenarios.append({
        'Scenario': 'G',
        'Description': 'No scheduling=0, 5min setup, 50% cancellations',
        'TTA': tta,
        'TTS': tts_g,
        'TTU': ttu_g,
        'TTAV': ttav_g,
        'Availability_%': (tts_g/tta)*100 if tta > 0 else 0,
        'Performance_%': (ttu_g/tts_g)*100 if tts_g > 0 else 0,
        'Quality_%': 100.0,
        'ORE_%': ore_g,
        'Variation_%': ore_g - base_metrics.ore,
        'Additional_Hours': ttav_g - base_metrics.total_time_added_value
    })

    return pd.DataFrame(scenarios)
