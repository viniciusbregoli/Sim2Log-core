Data Models
===========

.. currentmodule:: models

This module contains all data classes used throughout the framework.

Configuration
-------------

SimulationConfig
^^^^^^^^^^^^^^^^

.. autoclass:: SimulationConfig
   :members:
   :undoc-members:
   :show-inheritance:

Results
-------

ProcessModel
^^^^^^^^^^^^

.. autoclass:: ProcessModel
   :members:
   :undoc-members:
   :show-inheritance:

SimulationResult
^^^^^^^^^^^^^^^^

.. autoclass:: SimulationResult
   :members:
   :undoc-members:
   :show-inheritance:

ValidationResult
^^^^^^^^^^^^^^^^

.. autoclass:: ValidationResult
   :members:
   :undoc-members:
   :show-inheritance:

Statistics
----------

ActivityStatistics
^^^^^^^^^^^^^^^^^^

.. autoclass:: ActivityStatistics
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

   from models import SimulationConfig, ProcessModel, SimulationResult

   # Create simulation configuration
   config = SimulationConfig(
       num_cases=1000,
       arrival_rate=5.0,
       random_seed=42
   )

   # ProcessModel is returned by ProcessMiner
   model: ProcessModel  # from miner.mine_process()

   # Access model attributes
   print(f"Activities: {len(model.activities)}")
   print(f"Petri net places: {len(model.petri_net.places)}")
   print(f"Petri net transitions: {len(model.petri_net.transitions)}")
   print(f"Quality: {model.quality_metrics}")

   # SimulationResult is returned by LogSimulator
   result: SimulationResult  # from simulator.simulate()

   # Access simulation results
   print(f"Generated XES: {result.xes_path}")
   print(f"Cases: {result.num_cases}")
   print(f"Duration: {result.total_duration:.2f}s")
