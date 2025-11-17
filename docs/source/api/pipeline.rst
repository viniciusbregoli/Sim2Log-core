Pipeline - Unified API
======================

.. currentmodule:: pipeline

The :class:`ProcessMiningPipeline` class provides a high-level facade that integrates all components.

ProcessMiningPipeline
---------------------

.. autoclass:: ProcessMiningPipeline
   :members:
   :undoc-members:
   :show-inheritance:

Helper Functions
----------------

.. autofunction:: quick_analysis

Example Usage
-------------

Complete Workflow
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pipeline import ProcessMiningPipeline

   # Initialize
   pipeline = ProcessMiningPipeline(verbose=True)

   # Run full pipeline
   results = pipeline.run_full_pipeline(
       "hospital_log.xes",
       variant_filter=0.8,
       num_simulated_cases=500
   )

   # Access results
   ore_metrics = results['ore_metrics']
   process_model = results['process_model']
   validation = results['validation_result']

   print(f"ORE: {ore_metrics.ore:.1f}%")
   print(f"Fitness: {process_model.quality_metrics['fitness']:.3f}")
   print(f"Similarity: {validation.similarity_percentage:.1f}%")

Step-by-Step
^^^^^^^^^^^^

.. code-block:: python

   pipeline = ProcessMiningPipeline()

   # Step 1: Analyze
   profile = pipeline.analyze_log("log.xes")

   # Step 2: Mine
   model = pipeline.mine_process("log.xes", variant_filter=0.9)

   # Step 3: Simulate
   simulation = pipeline.simulate(model, num_cases=200)

   # Step 4: Validate
   validation = pipeline.validate("log.xes", simulation.xes_path)

   # Step 5: ORE
   ore = pipeline.calculate_ore("log.xes")
