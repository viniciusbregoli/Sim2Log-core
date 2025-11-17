Component Diagrams
==================

This section presents the component diagrams for the Sim2Log architecture, inspired by the computational simulation methodology.

Architecture Overview
---------------------

The following diagram shows the complete data flow through all five modules:

.. uml:: diagrams_architecture.puml
   :caption: Figura 1 - Arquitetura Geral Sim2Log - Fluxo de Dados Completo

The architecture follows a pipeline pattern where each module processes data and passes results to the next stage.

Individual Component Diagrams
------------------------------

ProcessMiningPipeline
^^^^^^^^^^^^^^^^^^^^^

The main orchestrator that coordinates all modules:

.. uml:: diagrams_pipeline.puml
   :caption: Figura 2 - ProcessMiningPipeline - Fluxo Completo

**Key responsibilities:**
- Orchestrates the complete workflow
- Manages data flow between modules
- Provides unified API for all operations

LogAnalyzer
^^^^^^^^^^^

Analyzes and profiles event logs to detect characteristics and validate format:

.. uml:: diagrams_analyzer.puml
   :caption: Figura 3 - LogAnalyzer - Análise e Perfil do Log

**Inputs:**
- Event log in XES format
- Traces, events, attributes, and extensions
- Timestamps and resource information

**Analysis methods:**
- Auto-detection of log structure
- Process variant identification
- Statistical analysis
- Format validation

**Outputs:**
- Log profile with trace/event counts
- Unique activities and resources
- Process variants
- Column mappings (activities, timestamps, resources)
- Sim2Log compatibility status
- Temporal statistics

ProcessMiner
^^^^^^^^^^^^

Discovers process models from event logs using the Inductive Miner algorithm:

.. uml:: diagrams_process_miner.puml
   :caption: Figura 4 - ProcessMiner - Descoberta de Modelo

**Inputs:**
- Event log with traces, activities, timestamps
- Configuration parameters (variant filter, algorithm settings)

**Outputs:**
- Petri Net and Process Tree representations
- Quality metrics (Fitness, Precision, Simplicity)
- Activity duration distributions
- Arrival rate statistics

LogSimulator
^^^^^^^^^^^^

Generates synthetic event logs through discrete-event simulation:

.. uml:: diagrams_simulator.puml
   :caption: Figura 5 - LogSimulator - Simulação Computacional

**Inputs:**
- Process model (tree structure)
- Activity distributions and timing information
- Arrival rates and resource constraints
- Current state and statistics

**Simulation engines:**
- SimPy for discrete-event simulation
- Distribution generators for realistic timing

**Outputs:**
- Synthetic event logs in XES and CSV formats
- Execution statistics

LogValidator
^^^^^^^^^^^^

Validates synthetic logs against original logs using statistical methods:

.. uml:: diagrams_validator.puml
   :caption: Figura 6 - LogValidator - Comparação e Validação

**Comparison methods:**
- Activity distribution comparison
- Variant distribution analysis
- Duration distribution analysis
- Kolmogorov-Smirnov statistical test

**Outputs:**
- Similarity percentage
- Detailed comparison metrics
- Statistical test results

Diagram Conventions
-------------------

The diagrams follow these conventions:

- **Central component** (blue): Main processing unit
- **Left side**: Primary inputs and data sources
- **Top**: Configuration and validation parameters
- **Bottom**: Processing engines and algorithms
- **Right side**: Outputs and results

This layout is inspired by computational simulation methodologies, emphasizing the flow of data through transformation stages.

Rendering the Diagrams
-----------------------

These diagrams are written in PlantUML format. To render them:

**Using PlantUML:**

.. code-block:: bash

   # Install PlantUML
   sudo apt-get install plantuml

   # Render a diagram
   plantuml diagrams_architecture.puml

**Using Sphinx with sphinxcontrib-plantuml:**

.. code-block:: bash

   uv pip install sphinxcontrib-plantuml

   # Add to conf.py:
   extensions = ['sphinxcontrib.plantuml']

**Online rendering:**

Visit https://www.plantuml.com/plantuml/uml/ and paste the diagram code.
