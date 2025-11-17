"""
Sim2Log Core - Process Mining to Simulation Pipeline.

This package provides modular components for process mining workflows:

- **Analysis** (:class:`log_analyzer.LogAnalyzer`): Detect log characteristics
- **Mining** (:class:`process_mining.ProcessMiner`): Discover process models
- **Simulation** (:class:`simulation.LogSimulator`): Generate synthetic logs
- **Validation** (:class:`validation.LogValidator`): Compare logs
- **ORE Calculation** (:class:`ore_indicators.ORECalculator`): Compute effectiveness metrics

Each component works independently or as part of the unified pipeline.

Quick Start:
    Use the facade for complete workflow::

        from pipeline import ProcessMiningPipeline

        pipeline = ProcessMiningPipeline()
        results = pipeline.run_full_pipeline("mylog.xes")

    Or use individual components::

        from log_analyzer import LogAnalyzer
        from process_mining import ProcessMiner

        analyzer = LogAnalyzer()
        profile = analyzer.analyze("mylog.xes")

        miner = ProcessMiner()
        model = miner.mine_process("mylog.xes")
"""

# High-level API
from .pipeline import ProcessMiningPipeline, quick_analysis

# Individual components
from .log_analyzer import LogAnalyzer, LogProfile
from .process_mining import ProcessMiner
from .simulation import LogSimulator
from .validation import LogValidator
from .ore_indicators import ORECalculator, OREMetrics

# Data models
from .models import (
    SimulationConfig,
    ActivityStatistics,
    ProcessModel,
    SimulationResult,
    ValidationResult,
)

__all__ = [
    # Main API
    'ProcessMiningPipeline',
    'quick_analysis',
    # Components
    'LogAnalyzer',
    'ProcessMiner',
    'LogSimulator',
    'LogValidator',
    'ORECalculator',
    # Data Models
    'LogProfile',
    'OREMetrics',
    'SimulationConfig',
    'ActivityStatistics',
    'ProcessModel',
    'SimulationResult',
    'ValidationResult',
]
