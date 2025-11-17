Quick Start Guide
=================

This guide shows the fastest way to get started with Sim2Log.

Installation
------------

Using uv (recommended):

.. code-block:: bash

   cd core
   uv pip install -e .

Using pip:

.. code-block:: bash

   pip install -e ./core

Dependencies
^^^^^^^^^^^^

Main dependencies (installed automatically):

- pm4py >= 2.7.0
- pandas >= 2.0.0
- simpy >= 4.0.0
- scipy >= 1.10.0

For documentation:

.. code-block:: bash

   uv pip install sphinx sphinx-rtd-theme

First Example - Complete Pipeline
----------------------------------

Run the full process mining workflow with one command:

.. code-block:: python

   from pipeline import ProcessMiningPipeline

   # Create pipeline
   pipeline = ProcessMiningPipeline(verbose=True)

   # Run everything
   results = pipeline.run_full_pipeline(
       "bases/xes/CirurgiasMarcoHucEnriched.xes",
       variant_filter=0.8,
       num_simulated_cases=100
   )

   # Print summary
   print(f"\n{'='*60}")
   print("RESULTS SUMMARY")
   print(f"{'='*60}")
   print(f"ORE: {results['ore_metrics'].ore:.1f}%")
   print(f"Fitness: {results['process_model'].quality_metrics['fitness']:.3f}")
   print(f"Validation: {results['validation_result'].similarity_percentage:.1f}%")
   print(f"Generated: {results['simulation_result'].xes_path}")

Second Example - Step by Step
------------------------------

Use individual modules for more control:

.. code-block:: python

   from log_analyzer import LogAnalyzer
   from process_mining import ProcessMiner
   from simulation import LogSimulator
   from validation import LogValidator
   from models import SimulationConfig

   log_path = "bases/xes/CirurgiasMarcoHucEnriched.xes"

   # Step 1: Analyze
   analyzer = LogAnalyzer()
   profile = analyzer.analyze(log_path)
   print(f"✓ Analyzed: {profile.num_traces} cases, {profile.num_unique_activities} activities")

   # Step 2: Mine
   miner = ProcessMiner()
   model = miner.mine_process(log_path, variant_filter=0.8)
   print(f"✓ Mined: Fitness={model.quality_metrics['fitness']:.3f}")

   # Step 3: Simulate
   config = SimulationConfig(num_cases=100, random_seed=42)
   simulator = LogSimulator(config)
   result = simulator.simulate(model, output_dir="outputs")
   print(f"✓ Simulated: {result.xes_path}")

   # Step 4: Validate
   validator = LogValidator()
   validation = validator.validate(log_path, result.xes_path)
   print(f"✓ Validated: {validation.similarity_percentage:.1f}% similar")

Third Example - ORE Only
-------------------------

Calculate effectiveness indicators without running other modules:

.. code-block:: python

   from ore_indicators import ORECalculator, calculate_ore_scenarios

   # Create calculator
   calc = ORECalculator(
       verbose=True,
       daily_hours=11.5,
       setup_time_minutes=15
   )

   # Calculate from enriched XES
   metrics = calc.calculate_from_log("bases/xes/CirurgiasMarcoHucEnriched.xes")

   # Display metrics
   print(f"\nORE: {metrics.ore:.1f}%")
   print(f"  Availability:  {metrics.availability:.1f}%")
   print(f"  Performance:   {metrics.performance:.1f}%")
   print(f"  Quality:       {metrics.quality:.1f}%")

   print(f"\nSurgeries:")
   print(f"  Completed:     {metrics.num_surgeries_completed}")
   print(f"  Cancelled:     {metrics.num_surgeries_cancelled} ({metrics.cancellation_rate:.1f}%)")

   # Generate improvement scenarios
   scenarios = calculate_ore_scenarios(metrics)
   print(f"\n{scenarios}")

Using Streamlit App
-------------------

Sim2Log includes a web interface:

.. code-block:: bash

   cd core/app
   uv run streamlit run app.py

Then:

1. Upload XES file in sidebar
2. Run analysis (Tab 1)
3. Run process mining (Tab 2)
4. Run simulation (Tab 3)
5. View validation (Tab 4)
6. Calculate ORE (Tab 6)

Converting Excel to Enriched XES
---------------------------------

For better ORE accuracy, convert Excel data to enriched XES:

.. code-block:: bash

   cd core
   uv run python converters/convert_xlsx_to_xes.py \\
       bases/CirurgiasMarcoHuc.xlsx \\
       bases/xes/CirurgiasMarcoHucEnriched.xes

The enriched XES includes:

- ``surgery:status`` - Surgery status (Realizada/Cancelada)
- ``surgery:duration_real_minutes`` - Actual duration
- ``surgery:cancellation_reason`` - Why cancelled
- ``surgery:scheduled_date`` - When scheduled

Next Steps
----------

- Read the :doc:`modules` overview to understand each component
- Check :doc:`examples` for more use cases
- Browse the :doc:`api/pipeline` reference
- Learn about :doc:`enriched_xes` format
