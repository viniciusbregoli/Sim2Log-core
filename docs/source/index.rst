.. Sim2Log documentation master file

================================
Sim2Log - Process Mining Pipeline
================================

**Sim2Log** is a modular process mining framework that transforms event logs into actionable insights through discovery, simulation, and validation.

.. image:: https://img.shields.io/badge/python-3.11+-blue.svg
   :alt: Python Version

Features
========

✅ **Modular Architecture** - Each component works independently

✅ **Domain-Agnostic** - Works with any XES log (healthcare, finance, manufacturing, etc.)

✅ **Complete Workflow** - Analysis → Mining → Simulation → Validation → ORE

✅ **Real Data Support** - Enriched XES format with operational attributes

✅ **High-Quality Models** - Inductive Miner with quality metrics (Fitness, Precision, Simplicity)

Quick Start
===========

Installation
------------

.. code-block:: bash

   uv pip install -e .

Basic Usage
-----------

**Option 1: Complete Pipeline**

.. code-block:: python

   from pipeline import ProcessMiningPipeline

   # Create pipeline
   pipeline = ProcessMiningPipeline(verbose=True)

   # Run complete workflow
   results = pipeline.run_full_pipeline("hospital_log.xes")

   # Access results
   print(f"ORE: {results['ore_metrics'].ore:.1f}%")
   print(f"Fitness: {results['process_model'].quality_metrics['fitness']:.3f}")
   print(f"Validation: {results['validation_result'].similarity_percentage:.1f}%")

**Option 2: Individual Components**

.. code-block:: python

   from log_analyzer import LogAnalyzer
   from process_mining import ProcessMiner
   from simulation import LogSimulator
   from validation import LogValidator
   from ore_indicators import ORECalculator

   # Step 1: Analyze
   analyzer = LogAnalyzer()
   profile = analyzer.analyze("log.xes")
   print(f"Cases: {profile.num_traces}, Activities: {profile.num_unique_activities}")

   # Step 2: Mine
   miner = ProcessMiner()
   model = miner.mine_process("log.xes", variant_filter=0.8)
   print(f"Fitness: {model.quality_metrics['fitness']:.3f}")

   # Step 3: Simulate
   config = SimulationConfig(num_cases=100)
   simulator = LogSimulator(config)
   result = simulator.simulate(model)
   print(f"Generated: {result.xes_path}")

   # Step 4: Validate
   validator = LogValidator()
   validation = validator.validate("log.xes", result.xes_path)
   print(f"Similarity: {validation.similarity_percentage:.1f}%")

   # Step 5: ORE
   ore_calc = ORECalculator()
   ore = ore_calc.calculate_from_log("log.xes")
   print(f"ORE: {ore.ore:.1f}%")

Architecture
============

The framework consists of 5 independent modules:

1. **LogAnalyzer** - Detects log characteristics (activities, timestamps, resources, variants)
2. **ProcessMiner** - Discovers Petri Nets and Process Trees using Inductive Miner
3. **LogSimulator** - Generates synthetic logs using SimPy discrete-event simulation
4. **LogValidator** - Compares logs using distribution similarity metrics
5. **ORECalculator** - Computes Operating Room Effectiveness (or any process effectiveness)

Each module can be used standalone or combined via ``ProcessMiningPipeline``.

Documentation Contents
======================

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   quickstart
   modules
   diagrams
   examples
   enriched_xes

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/pipeline
   api/log_analyzer
   api/process_mining
   api/simulation
   api/validation
   api/ore_indicators
   api/models

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   changelog
   contributing


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
