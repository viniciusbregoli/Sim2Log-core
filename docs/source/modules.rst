Modules Overview
================

Sim2Log consists of 5 independent, modular components that can be used together or separately.

Core Modules
------------

1. LogAnalyzer - Log Profiling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Detect and validate log characteristics

**Key Features**:
- Auto-detects activities, timestamps, resources
- Identifies process variants
- Validates Sim2Log compatibility
- Works with any XES format

**When to use**: First step to understand your log structure

**Example**:

.. code-block:: python

   from log_analyzer import LogAnalyzer

   analyzer = LogAnalyzer()
   profile = analyzer.analyze("mylog.xes")
   print(f"Activities: {profile.num_unique_activities}")


2. ProcessMiner - Model Discovery
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Discover process models (Petri Nets, Process Trees)

**Key Features**:
- Inductive Miner algorithm
- Quality metrics (Fitness, Precision, Simplicity)
- Activity duration distributions
- Arrival rate detection

**When to use**: After analysis, to discover the process structure

**Example**:

.. code-block:: python

   from process_mining import ProcessMiner

   miner = ProcessMiner()
   model = miner.mine_process("mylog.xes", variant_filter=0.8)
   print(f"Fitness: {model.quality_metrics['fitness']:.3f}")


3. LogSimulator - Synthetic Log Generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Generate realistic synthetic event logs

**Key Features**:
- SimPy discrete-event simulation
- Process Tree replay
- Statistical duration distributions
- Resource allocation

**When to use**: To generate test data or augment sparse logs

**Example**:

.. code-block:: python

   from simulation import LogSimulator
   from models import SimulationConfig

   config = SimulationConfig(num_cases=500)
   simulator = LogSimulator(config)
   result = simulator.simulate(model)


4. LogValidator - Quality Assessment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Compare original and synthetic logs

**Key Features**:
- Activity distribution comparison
- Variant distribution comparison
- Duration distribution comparison
- Kolmogorov-Smirnov statistical test

**When to use**: After simulation, to validate synthetic log quality

**Example**:

.. code-block:: python

   from validation import LogValidator

   validator = LogValidator()
   result = validator.validate("original.xes", "synthetic.xes")
   print(f"Similarity: {result.similarity_percentage:.1f}%")


5. ORECalculator - Effectiveness Metrics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Calculate process effectiveness indicators

**Key Features**:
- ORE = Availability × Performance × Quality
- Loss breakdown (setup, cancellations, variation, etc.)
- Improvement scenarios
- Supports enriched XES with operational data

**When to use**: To measure and improve process efficiency

**Example**:

.. code-block:: python

   from ore_indicators import ORECalculator

   calc = ORECalculator()
   metrics = calc.calculate_from_log("log.xes")
   print(f"ORE: {metrics.ore:.1f}%")


Unified Pipeline
----------------

For convenience, use the high-level facade:

.. code-block:: python

   from pipeline import ProcessMiningPipeline

   pipeline = ProcessMiningPipeline()
   results = pipeline.run_full_pipeline("mylog.xes")

This executes all 5 modules in sequence and returns all results.

Module Independence
-------------------

Each module is **fully independent**:

- ✅ Can be imported separately
- ✅ Has its own configuration
- ✅ Works with standard XES format
- ✅ No dependencies between modules (except data models)

Example of using modules independently:

.. code-block:: python

   # Use only analysis
   from log_analyzer import LogAnalyzer
   analyzer = LogAnalyzer()
   profile = analyzer.analyze("log.xes")

   # Use only ORE calculation
   from ore_indicators import ORECalculator
   calc = ORECalculator()
   ore = calc.calculate_from_log("enriched_log.xes")

   # Use only simulation (with pre-existing model)
   from simulation import LogSimulator
   simulator = LogSimulator(config)
   result = simulator.simulate(existing_model)
