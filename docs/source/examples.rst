Examples
========

Healthcare - Surgical Process
------------------------------

Complete analysis of surgical center operations:

.. code-block:: python

   from pipeline import ProcessMiningPipeline

   # Setup
   pipeline = ProcessMiningPipeline(
       verbose=True,
       daily_hours=11.5,        # 07:30-19:00
       setup_time_minutes=15    # Room turnover
   )

   # Run pipeline
   results = pipeline.run_full_pipeline(
       "hospital_surgeries.xes",
       variant_filter=0.8,
       num_simulated_cases=500
   )

   # Analyze ORE
   ore = results['ore_metrics']
   print(f"ORE: {ore.ore:.1f}%")
   print(f"Cancellation rate: {ore.cancellation_rate:.1f}%")
   print(f"Loss from cancellations: {ore.loss_cancellations:.1f}h")

Financial - Loan Approval
--------------------------

Mining loan approval process:

.. code-block:: python

   from process_mining import ProcessMiner

   miner = ProcessMiner(verbose=True)
   model = miner.mine_process(
       "loan_approvals.xes",
       variant_filter=0.9,  # Stricter filter
       save_model_image="loan_process.png"
   )

   # Check quality
   print(f"Fitness: {model.quality_metrics['fitness']:.3f}")
   print(f"Precision: {model.quality_metrics['precision']:.3f}")

   # Analyze approval times
   for activity, stats in model.activities.items():
       if "approval" in activity.lower():
           print(f"{activity}: {stats.mean_duration/60:.1f} minutes avg")

Manufacturing - Production Line
--------------------------------

Simulating production scenarios:

.. code-block:: python

   from process_mining import ProcessMiner
   from simulation import LogSimulator
   from models import SimulationConfig

   # Mine existing process
   miner = ProcessMiner()
   model = miner.mine_process("production_log.xes")

   # Simulate different scenarios
   for rate in [10, 15, 20, 25]:  # products per hour
       config = SimulationConfig(
           num_cases=1000,
           arrival_rate=rate/60,  # convert to per minute
           random_seed=42
       )

       simulator = LogSimulator(config)
       result = simulator.simulate(
           model,
           output_prefix=f"production_rate_{rate}"
       )

       print(f"Rate {rate}/h: Generated {result.num_cases} cases in {result.total_duration:.1f}s")

Retail - Order Fulfillment
---------------------------

Analyzing order processing with validation:

.. code-block:: python

   from log_analyzer import LogAnalyzer
   from process_mining import ProcessMiner
   from validation import LogValidator

   # Analyze original log
   analyzer = LogAnalyzer()
   profile = analyzer.analyze("orders.xes")

   print(f"Order variants: {profile.num_variants}")
   print(f"Most common variant: {profile.most_common_variants[0]}")

   # Mine and simulate
   miner = ProcessMiner()
   model = miner.mine_process("orders.xes")

   # ... simulate ...

   # Validate synthetic orders
   validator = LogValidator()
   result = validator.validate("orders.xes", "simulated_orders.xes")

   if result.similarity_percentage >= 80:
       print("✓ High-quality synthetic log")
   else:
       print(f"⚠ Similarity only {result.similarity_percentage:.1f}%")

Custom ORE for Any Process
---------------------------

ORE metrics work for any time-based process:

.. code-block:: python

   from ore_indicators import ORECalculator

   # For a customer service center (8h shifts)
   calc = ORECalculator(
       daily_hours=8.0,
       setup_time_minutes=5,  # Agent prep time
       verbose=True
   )

   metrics = calc.calculate_from_log("customer_service.xes")

   print(f"Service Effectiveness: {metrics.ore:.1f}%")
   print(f"  Availability:  {metrics.availability:.1f}%")
   print(f"  Performance:   {metrics.performance:.1f}%")
   print(f"  Quality:       {metrics.quality:.1f}%")

Batch Processing
----------------

Process multiple logs programmatically:

.. code-block:: python

   from pathlib import Path
   from pipeline import ProcessMiningPipeline
   import pandas as pd

   pipeline = ProcessMiningPipeline(verbose=False)

   results_summary = []

   for log_path in Path("logs").glob("*.xes"):
       print(f"Processing {log_path.name}...")

       try:
           results = pipeline.run_full_pipeline(
               log_path,
               variant_filter=0.8,
               num_simulated_cases=100
           )

           results_summary.append({
               'log': log_path.name,
               'cases': results['log_profile'].num_traces,
               'activities': results['log_profile'].num_unique_activities,
               'fitness': results['process_model'].quality_metrics['fitness'],
               'precision': results['process_model'].quality_metrics['precision'],
               'similarity': results['validation_result'].similarity_percentage,
               'ore': results['ore_metrics'].ore
           })
       except Exception as e:
           print(f"  Error: {e}")
           continue

   # Save summary
   df = pd.DataFrame(results_summary)
   df.to_csv("batch_results.csv", index=False)
   print(f"\nProcessed {len(df)} logs successfully")
