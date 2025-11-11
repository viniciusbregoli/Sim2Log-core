"""
Modelos de dados para o Sim2Log Core.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


@dataclass
class SimulationConfig:
    """Configuração para a simulação de logs."""
    
    num_cases: int = 100
    """Número de casos (traces) a serem gerados."""
    
    arrival_rate: Optional[float] = None
    """Taxa de chegada de casos em minutos. Se None, usa a do log original."""
    
    activity_durations: Optional[Dict[str, float]] = None
    """Duração customizada de atividades em segundos. Se None, usa as originais."""
    
    variant_filter_percentage: float = 0.8
    """Percentual de variantes a manter (0.0 a 1.0)."""
    
    random_seed: int = 42
    """Seed para reprodutibilidade."""
    
    max_trace_length: int = 1000
    """Comprimento máximo de um trace."""


@dataclass
class ActivityStatistics:
    """Estatísticas de uma atividade."""
    
    name: str
    mean_duration: float
    durations: List[float]
    distribution_name: str
    distribution_params: Tuple
    p_value: float


@dataclass
class ProcessModel:
    """Modelo de processo extraído."""

    petri_net: object
    """Rede de Petri (pm4py object)."""

    initial_marking: object
    """Marcação inicial."""

    final_marking: object
    """Marcação final."""

    activities: Dict[str, ActivityStatistics]
    """Estatísticas das atividades."""

    arrival_rate: float
    """Taxa de chegada em minutos."""

    dispersion_rate: float
    """Taxa de dispersão em minutos."""

    median_case_duration: float
    """Duração mediana dos casos."""

    num_cases: int
    """Número de casos no log original."""

    num_variants: int
    """Número de variantes após filtragem."""

    quality_metrics: Dict[str, float] = field(default_factory=dict)
    """Métricas de qualidade (fitness, precision, etc)."""

    resources: Optional[Dict[str, List[str]]] = None
    """Recursos por atividade."""

    log_profile: Optional[object] = None
    """Perfil do log original (LogProfile)."""

    process_tree: Optional[object] = None
    """Process Tree (pm4py ProcessTree object)."""


@dataclass
class SimulationResult:
    """Resultado da simulação."""
    
    csv_path: Path
    """Caminho do arquivo CSV gerado."""
    
    xes_path: Path
    """Caminho do arquivo XES gerado."""
    
    num_cases_generated: int
    """Número de casos gerados."""
    
    num_events_generated: int
    """Número de eventos gerados."""
    
    simulation_time: float
    """Tempo de simulação em segundos."""
    
    validation_metrics: Optional[Dict[str, float]] = None
    """Métricas de validação (se executada)."""
    
    timestamp: datetime = field(default_factory=datetime.now)
    """Timestamp da geração."""


@dataclass
class ValidationResult:
    """Resultado da validação."""
    
    fitness: float
    """Fitness médio (0-1, quanto maior melhor)."""
    
    cost: float
    """Custo médio de alinhamento (quanto menor melhor)."""
    
    similarity_percentage: float
    """Percentual de similaridade."""
    
    details: Dict = field(default_factory=dict)
    """Detalhes adicionais da validação."""

