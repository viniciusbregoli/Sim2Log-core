"""
Process Mining Pipeline - Unified API for all modules.

This module provides a high-level facade that integrates all components:
analysis, mining, simulation, validation, and ORE calculation.

Example:
    Basic usage::

        from pipeline import ProcessMiningPipeline

        # Create pipeline
        pipeline = ProcessMiningPipeline()

        # Run full pipeline
        results = pipeline.run_full_pipeline("log.xes")

        # Access results
        print(f"ORE: {results['ore_metrics'].ore:.1f}%")
        print(f"Fitness: {results['process_model'].quality_metrics['fitness']:.3f}")

    Step-by-step usage::

        pipeline = ProcessMiningPipeline()

        # Step 1: Analyze
        profile = pipeline.analyze_log("log.xes")

        # Step 2: Mine process
        model = pipeline.mine_process("log.xes")

        # Step 3: Simulate
        simulation = pipeline.simulate(model, num_cases=100)

        # Step 4: Validate
        validation = pipeline.validate("log.xes", simulation.xes_path)

        # Step 5: Calculate ORE
        ore = pipeline.calculate_ore("log.xes")
"""

from pathlib import Path
from typing import Dict, Optional, Any

from log_analyzer import LogAnalyzer, LogProfile
from process_mining import ProcessMiner
from simulation import LogSimulator
from validation import LogValidator
from ore_indicators import ORECalculator, OREMetrics
from models import (
    ProcessModel,
    SimulationConfig,
    SimulationResult,
    ValidationResult,
)


class ProcessMiningPipeline:
    """
    High-level facade for process mining workflow.

    Integrates all modules into a unified API:
    - Log Analysis (LogAnalyzer)
    - Process Mining (ProcessMiner)
    - Log Simulation (LogSimulator)
    - Validation (LogValidator)
    - ORE Calculation (ORECalculator)

    All methods work independently - you can use any subset of functionality.

    Attributes:
        analyzer (LogAnalyzer): Log analysis component
        miner (ProcessMiner): Process mining component
        simulator (LogSimulator): Simulation component
        validator (LogValidator): Validation component
        ore_calculator (ORECalculator): ORE calculation component
        verbose (bool): Whether to print progress messages

    Example:
        >>> pipeline = ProcessMiningPipeline(verbose=True)
        >>> results = pipeline.run_full_pipeline("hospital_log.xes")
        >>> print(f"ORE: {results['ore_metrics'].ore:.1f}%")
    """

    def __init__(
        self,
        verbose: bool = True,
        daily_hours: float = 11.5,
        setup_time_minutes: float = 15.0
    ):
        """
        Initialize pipeline with all components.

        Args:
            verbose: If True, print progress messages during processing
            daily_hours: Operating hours per day (for ORE calculation)
            setup_time_minutes: Average setup time between activities (for ORE)

        Example:
            >>> pipeline = ProcessMiningPipeline(verbose=True)
            >>> pipeline = ProcessMiningPipeline(verbose=False, daily_hours=8.0)
        """
        self.verbose = verbose

        # Initialize all components
        self.analyzer = LogAnalyzer(verbose=verbose)
        self.miner = ProcessMiner(verbose=verbose)
        self.validator = LogValidator(verbose=verbose)
        self.ore_calculator = ORECalculator(
            verbose=verbose,
            daily_hours=daily_hours,
            setup_time_minutes=setup_time_minutes
        )

        # Simulator is created on-demand with specific config
        self._simulator: Optional[LogSimulator] = None

    def analyze_log(self, log_path: Path | str) -> LogProfile:
        """
        Analyze log structure and characteristics.

        This is typically the first step - it detects:
        - Number of cases, events, activities
        - Available attributes (timestamps, resources, etc.)
        - Process variants and their frequencies
        - Temporal characteristics

        Args:
            log_path: Path to XES log file

        Returns:
            LogProfile with detected characteristics

        Raises:
            FileNotFoundError: If log file doesn't exist

        Example:
            >>> profile = pipeline.analyze_log("hospital.xes")
            >>> print(f"Cases: {profile.num_traces}")
            >>> print(f"Activities: {profile.num_unique_activities}")
            >>> print(f"Has resources: {profile.has_resources}")
        """
        return self.analyzer.analyze(log_path)

    def mine_process(
        self,
        log_path: Path | str,
        variant_filter: float = 0.8,
        save_model_image: Optional[Path] = None,
        auto_detect: bool = True
    ) -> ProcessModel:
        """
        Mine process model from event log.

        Discovers Petri Net and Process Tree using Inductive Miner.
        Extracts activity statistics, arrival rates, and quality metrics.

        Args:
            log_path: Path to XES log file
            variant_filter: Keep top X% of variants (0.0 to 1.0)
            save_model_image: If provided, save Petri Net visualization
            auto_detect: If True, detect and validate log characteristics

        Returns:
            ProcessModel with Petri Net, statistics, and quality metrics

        Raises:
            FileNotFoundError: If log file doesn't exist
            ValueError: If log is incompatible

        Example:
            >>> model = pipeline.mine_process("log.xes", variant_filter=0.9)
            >>> print(f"Fitness: {model.quality_metrics['fitness']:.3f}")
            >>> print(f"Activities: {len(model.activities)}")
            >>> print(f"Arrival rate: {model.arrival_rate:.2f} cases/min")
        """
        return self.miner.mine_process(
            log_path=log_path,
            variant_filter=variant_filter,
            save_model_image=save_model_image,
            auto_detect=auto_detect
        )

    def simulate(
        self,
        process_model: ProcessModel,
        num_cases: int = 100,
        arrival_rate: Optional[float] = None,
        output_dir: Optional[Path] = None,
        output_prefix: str = "simulated",
        random_seed: int = 42
    ) -> SimulationResult:
        """
        Generate synthetic log from process model.

        Creates new event log by simulating the discovered process.
        Uses activity duration distributions and arrival patterns.

        Args:
            process_model: Process model from mine_process()
            num_cases: Number of cases to simulate
            arrival_rate: Case arrival rate (cases/min), uses model's rate if None
            output_dir: Directory for output files (default: current/outputs)
            output_prefix: Prefix for output filenames
            random_seed: Random seed for reproducibility

        Returns:
            SimulationResult with paths to generated XES and CSV files

        Example:
            >>> model = pipeline.mine_process("log.xes")
            >>> result = pipeline.simulate(model, num_cases=500)
            >>> print(f"Generated: {result.xes_path}")
            >>> print(f"Duration: {result.total_duration:.2f}s")
        """
        config = SimulationConfig(
            num_cases=num_cases,
            arrival_rate=arrival_rate,
            random_seed=random_seed
        )

        self._simulator = LogSimulator(config, verbose=self.verbose)

        if output_dir is None:
            output_dir = Path("outputs")

        return self._simulator.simulate(
            process_model,
            output_dir=output_dir,
            output_prefix=output_prefix
        )

    def validate(
        self,
        original_log_path: Path | str,
        simulated_log_path: Path | str
    ) -> ValidationResult:
        """
        Compare original and simulated logs.

        Validates quality of synthetic log by comparing:
        - Activity distributions
        - Variant distributions
        - Duration distributions
        - Statistical similarity (KS test)

        Args:
            original_log_path: Path to original XES log
            simulated_log_path: Path to simulated XES log

        Returns:
            ValidationResult with similarity scores and statistics

        Example:
            >>> validation = pipeline.validate("original.xes", "simulated.xes")
            >>> print(f"Similarity: {validation.similarity_percentage:.1f}%")
            >>> print(f"Activity match: {validation.activity_distribution_similarity:.3f}")
        """
        return self.validator.validate(original_log_path, simulated_log_path)

    def calculate_ore(self, log_path: Path | str) -> OREMetrics:
        """
        Calculate Operating Room Effectiveness indicators.

        Computes ORE metrics following lean healthcare methodology:
        - Availability: Scheduled time / Total time
        - Performance: Used time / Scheduled time
        - Quality: Added value time / Used time
        - ORE = Availability × Performance × Quality

        Args:
            log_path: Path to XES log file (preferably enriched with operational data)

        Returns:
            OREMetrics with all indicators and loss breakdown

        Example:
            >>> metrics = pipeline.calculate_ore("enriched_log.xes")
            >>> print(f"ORE: {metrics.ore:.1f}%")
            >>> print(f"Cancellations: {metrics.num_surgeries_cancelled}")
            >>> print(f"Cancellation rate: {metrics.cancellation_rate:.1f}%")
        """
        return self.ore_calculator.calculate_from_log(log_path)

    def run_full_pipeline(
        self,
        log_path: Path | str,
        variant_filter: float = 0.8,
        num_simulated_cases: int = 100,
        output_dir: Optional[Path] = None,
        save_model_image: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Execute complete process mining pipeline.

        Runs all steps in sequence:
        1. Log analysis
        2. Process mining
        3. Simulation
        4. Validation
        5. ORE calculation

        Args:
            log_path: Path to XES log file
            variant_filter: Keep top X% of variants (0.0 to 1.0)
            num_simulated_cases: Number of cases to simulate
            output_dir: Directory for outputs (default: current/outputs)
            save_model_image: If provided, save Petri Net visualization

        Returns:
            Dictionary with all results:
                - 'log_profile': LogProfile
                - 'process_model': ProcessModel
                - 'simulation_result': SimulationResult
                - 'validation_result': ValidationResult
                - 'ore_metrics': OREMetrics

        Example:
            >>> results = pipeline.run_full_pipeline("hospital.xes")
            >>> print(f"ORE: {results['ore_metrics'].ore:.1f}%")
            >>> print(f"Fitness: {results['process_model'].quality_metrics['fitness']:.3f}")
            >>> print(f"Validation: {results['validation_result'].similarity_percentage:.1f}%")
        """
        if self.verbose:
            print("\n" + "=" * 70)
            print("PROCESS MINING PIPELINE")
            print("=" * 70)

        # Step 1: Analyze
        if self.verbose:
            print("\n[1/5] Analyzing log...")
        log_profile = self.analyze_log(log_path)

        # Step 2: Mine
        if self.verbose:
            print("\n[2/5] Mining process model...")
        process_model = self.mine_process(
            log_path,
            variant_filter=variant_filter,
            save_model_image=save_model_image
        )

        # Step 3: Simulate
        if self.verbose:
            print("\n[3/5] Simulating synthetic log...")
        simulation_result = self.simulate(
            process_model,
            num_cases=num_simulated_cases,
            output_dir=output_dir
        )

        # Step 4: Validate
        if self.verbose:
            print("\n[4/5] Validating synthetic log...")
        validation_result = self.validate(log_path, simulation_result.xes_path)

        # Step 5: ORE
        if self.verbose:
            print("\n[5/5] Calculating ORE indicators...")
        ore_metrics = self.calculate_ore(log_path)

        if self.verbose:
            print("\n" + "=" * 70)
            print("PIPELINE COMPLETED")
            print("=" * 70)
            print(f"\nORE: {ore_metrics.ore:.1f}%")
            print(f"Fitness: {process_model.quality_metrics['fitness']:.3f}")
            print(f"Validation Similarity: {validation_result.similarity_percentage:.1f}%")

        return {
            'log_profile': log_profile,
            'process_model': process_model,
            'simulation_result': simulation_result,
            'validation_result': validation_result,
            'ore_metrics': ore_metrics,
        }


# Convenience function for quick testing
def quick_analysis(log_path: Path | str) -> Dict[str, Any]:
    """
    Quick analysis of a log file (analysis + mining only).

    Args:
        log_path: Path to XES log file

    Returns:
        Dictionary with 'log_profile' and 'process_model'

    Example:
        >>> from pipeline import quick_analysis
        >>> results = quick_analysis("mylog.xes")
        >>> print(results['process_model'].quality_metrics)
    """
    pipeline = ProcessMiningPipeline(verbose=True)
    profile = pipeline.analyze_log(log_path)
    model = pipeline.mine_process(log_path)

    return {
        'log_profile': profile,
        'process_model': model
    }
