"""
Sim2Log Core - Gerador de Logs Sintéticos
=========================================

Core library para geração de logs sintéticos a partir de logs reais usando
Process Mining e Simulação de Eventos Discretos.

Principais componentes:
    - ProcessMiner: Extrai modelo de processo e parâmetros
    - LogSimulator: Executa simulação e gera logs sintéticos
    - LogValidator: Valida qualidade dos logs gerados
"""

from core.process_mining import ProcessMiner
from core.simulation import LogSimulator
from core.validation import LogValidator
from core.log_analyzer import LogAnalyzer, LogProfile, analyze_log
from core.models import SimulationConfig, ProcessModel, SimulationResult

__version__ = "2.0.0"
__all__ = [
    "ProcessMiner",
    "LogSimulator",
    "LogValidator",
    "LogAnalyzer",
    "LogProfile",
    "analyze_log",
    "SimulationConfig",
    "ProcessModel",
    "SimulationResult",
]

