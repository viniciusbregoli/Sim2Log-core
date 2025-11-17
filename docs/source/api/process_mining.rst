Process Mining - Model Discovery
=================================

.. currentmodule:: process_mining

The :class:`ProcessMiner` discovers Petri Nets and Process Trees from event logs.

ProcessMiner
------------

.. autoclass:: ProcessMiner
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

   from process_mining import ProcessMiner

   # Create miner
   miner = ProcessMiner(verbose=True)

   # Mine process model
   model = miner.mine_process(
       "hospital_log.xes",
       variant_filter=0.8,  # Keep top 80% variants
       save_model_image="model.png",
       auto_detect=True
   )

   # Access discovered model
   print(f"Activities: {len(model.activities)}")
   print(f"Fitness: {model.quality_metrics['fitness']:.3f}")
   print(f"Precision: {model.quality_metrics['precision']:.3f}")
   print(f"Simplicity: {model.quality_metrics['simplicity']:.3f}")

   # Access activity statistics
   for name, stats in model.activities.items():
       print(f"{name}: {stats.mean_duration:.1f}s avg, {stats.distribution_name}")

   # Access arrival rate
   print(f"Arrival rate: {model.arrival_rate:.2f} cases/min")

   # Use Petri Net for simulation or conformance checking
   petri_net = model.petri_net
   initial_marking = model.initial_marking
   final_marking = model.final_marking
