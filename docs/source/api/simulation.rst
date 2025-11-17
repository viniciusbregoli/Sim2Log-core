Simulation - Synthetic Log Generation
======================================

.. currentmodule:: simulation

The :class:`LogSimulator` generates synthetic event logs using discrete-event simulation.

LogSimulator
------------

.. autoclass:: LogSimulator
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

   from process_mining import ProcessMiner
   from simulation import LogSimulator
   from models import SimulationConfig

   # First, mine a model
   miner = ProcessMiner()
   model = miner.mine_process("original_log.xes")

   # Configure simulation
   config = SimulationConfig(
       num_cases=500,
       arrival_rate=5.0,  # 5 cases per minute
       random_seed=42
   )

   # Create simulator
   simulator = LogSimulator(config, verbose=True)

   # Run simulation
   result = simulator.simulate(
       model,
       output_dir="outputs",
       output_prefix="simulated"
   )

   # Access results
   print(f"Generated XES: {result.xes_path}")
   print(f"Generated CSV: {result.csv_path}")
   print(f"Simulated cases: {result.num_cases}")
   print(f"Simulation time: {result.total_duration:.2f}s")
