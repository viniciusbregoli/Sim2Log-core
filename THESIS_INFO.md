# Sim2Log-Core: Comprehensive Thesis Information File

**Generated**: 2025-11-17
**Project**: Sim2Log-Core - Process Mining, Simulation, and Validation Framework
**Repository**: https://github.com/viniciusbregoli/Sim2Log-core

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design](#architecture--design)
3. [Technology Stack](#technology-stack)
4. [Core Components](#core-components)
5. [Features & Capabilities](#features--capabilities)
6. [Data Flow & Workflow](#data-flow--workflow)
7. [Module Reference](#module-reference)
8. [APIs & Interfaces](#apis--interfaces)
9. [Configuration & Deployment](#configuration--deployment)
10. [Testing & Quality Assurance](#testing--quality-assurance)
11. [Research Contributions](#research-contributions)
12. [Future Directions](#future-directions)

---

## 1. Project Overview

### Executive Summary

**Sim2Log-Core** is a modular Python framework for process mining, simulation, and validation of event logs with specialized support for healthcare operational analytics. The project provides an integrated pipeline that combines:

- **Process Discovery**: Extract process models from event logs using machine learning
- **Synthetic Log Generation**: Create realistic synthetic logs based on discovered models
- **Quality Validation**: Compare synthetic logs against originals using alignment-based metrics
- **Operational Effectiveness Metrics**: Calculate healthcare-specific ORE indicators

### Primary Objectives

1. **Automate Process Discovery**: Extract Petri Nets and Process Trees from event logs using Inductive Miner algorithm
2. **Enable Simulation**: Generate synthetic but realistic event logs through discrete event simulation (SimPy)
3. **Validate Quality**: Assess synthetic log quality through fitness, precision, and alignment metrics
4. **Support Healthcare Analytics**: Calculate Operating Room Effectiveness (ORE) indicators based on Souza et al. (2020)
5. **Ensure Generality**: Support multiple domains (healthcare, finance, manufacturing, retail) with automatic log profiling
6. **Provide Accessibility**: Offer both programmatic API and web-based user interface

### Key Innovation

The framework unifies the complete process mining workflow in a single, cohesive system. Rather than requiring separate tools for mining, simulation, and validation, Sim2Log-Core provides:

- **Unified Pipeline**: Single entry point for complete analysis
- **Enriched XES Support**: Custom XML extensions for operational metadata (surgical status, cancellation reasons)
- **Domain-Specific Metrics**: ORE framework specifically designed for operating room analytics
- **Reproducible Simulation**: Seed-based random number generation for deterministic results
- **Multi-Modal Output**: Both programmatic API and interactive web interface

### Project Scope

```
┌─────────────────────────────────────────────────────────────┐
│                    Sim2Log-Core Scope                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  INPUT: Event Logs (XES format)                             │
│         ├─ Standard XES (process mining)                    │
│         └─ Enriched XES (healthcare with custom attributes) │
│                                                               │
│  PROCESSING:                                                │
│  1. Log Analysis & Profiling                               │
│  2. Process Model Discovery (Petri Nets + Process Trees)   │
│  3. Synthetic Log Generation (Discrete Event Simulation)   │
│  4. Quality Validation (Alignment-based metrics)           │
│  5. Healthcare Metrics (ORE indicators)                    │
│                                                               │
│  OUTPUT:                                                    │
│  ├─ Process Models (Petri Nets)                            │
│  ├─ Quality Metrics (fitness, precision, simplicity)       │
│  ├─ Synthetic Logs (XES, CSV)                              │
│  ├─ Validation Results (fitness, similarity)               │
│  └─ Healthcare Metrics (ORE percentages, loss breakdown)   │
│                                                               │
│  INTERFACES:                                               │
│  ├─ Python API (high-level facade pattern)                 │
│  └─ Web UI (Streamlit interactive dashboard)               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture & Design

### Architectural Philosophy

**Sim2Log-Core** follows a **layered, modular architecture** with clear separation of concerns:

```
┌────────────────────────────────────────────────────────────┐
│                   USER INTERFACE LAYER                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Streamlit Web Dashboard (app/app.py)                │  │
│  │  - File upload & management                          │  │
│  │  - Step-by-step execution                            │  │
│  │  - Interactive visualizations                        │  │
│  │  - Result export                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────────┐
│                   FACADE LAYER                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ProcessMiningPipeline                               │  │
│  │  - Orchestrates all components                       │  │
│  │  - Provides high-level API                           │  │
│  │  - Manages data flow between stages                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
         │    │    │      │       │
         ▼    ▼    ▼      ▼       ▼
┌────────────────────────────────────────────────────────────┐
│              COMPONENT LAYER (Independent Services)        │
├──────────────┬─────────────┬──────────┬──────────┬─────────┤
│ LogAnalyzer  │ProcessMiner │LogSimul- │LogVali- │ORECalc  │
│              │             │ator      │dator    │ulator   │
│ Profiling &  │ Discovery & │Event Log │Quality  │Healthcare│
│ Detection    │ Statistics  │Generation│Assurance│Metrics  │
└──────────────┴─────────────┴──────────┴─────────┴─────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│                 DATA MODELS LAYER (models.py)              │
│  - SimulationConfig                                        │
│  - ProcessModel, ActivityStatistics                        │
│  - SimulationResult, ValidationResult                      │
│  - OREMetrics                                              │
└────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│               INFRASTRUCTURE LAYER                          │
│  PM4Py | SimPy | Pandas | SciPy | NumPy                   │
└────────────────────────────────────────────────────────────┘
```

### Design Patterns

#### 1. **Facade Pattern**
The `ProcessMiningPipeline` class provides a unified, high-level interface to the complex subsystem:

```python
# Simple, unified interface
pipeline = ProcessMiningPipeline()
results = pipeline.run_full_pipeline("log.xes")

# Instead of:
# analyzer = LogAnalyzer()
# miner = ProcessMiner()
# simulator = LogSimulator(config)
# validator = LogValidator()
# calc = ORECalculator()
```

**Benefits**:
- Simplified client code
- Decoupling from internal complexity
- Easy workflow orchestration

#### 2. **Component-Based Architecture**
Each component is independent and testable:

```python
# Each component can be used standalone
analyzer = LogAnalyzer()
profile = analyzer.analyze("log.xes")

miner = ProcessMiner()
model = miner.mine_process("log.xes")

simulator = LogSimulator(config)
result = simulator.simulate(model)
```

**Benefits**:
- Modularity
- Reusability
- Independent testing
- Easy maintenance

#### 3. **Data Classes for Type Safety**
Strongly typed data structures ensure correctness:

```python
@dataclass
class ProcessModel:
    petri_net: object
    initial_marking: object
    final_marking: object
    activities: Dict[str, ActivityStatistics]
    arrival_rate: float
    # ... more fields
```

**Benefits**:
- Type hints for IDE support
- Self-documenting code
- Runtime validation possible

#### 4. **Strategy Pattern for Distribution Fitting**
Multiple fitting strategies tried in sequence:

```python
# Fits distribution to activity durations
# Tries: Normal → Lognormal → Exponential
# Selects best via Kolmogorov-Smirnov test
best_fit = fitter.fit(durations)
```

### Design Principles

| Principle | Implementation |
|-----------|-----------------|
| **Separation of Concerns** | Each module has single responsibility |
| **DRY (Don't Repeat Yourself)** | Utilities module for common functions |
| **Open/Closed** | Easy to extend without modifying existing code |
| **Dependency Inversion** | Components depend on abstractions (data classes) not implementations |
| **SOLID** | Single responsibility, dependency injection patterns |

---

## 3. Technology Stack

### Runtime Environment

| Component | Version | Rationale |
|-----------|---------|-----------|
| **Python** | 3.11.12+ | Modern Python with type hint support |
| **OS** | Cross-platform | Tested on Linux, Windows, macOS |

### Core Dependencies

#### Process Mining & Analysis
| Package | Version | Purpose |
|---------|---------|---------|
| **PM4Py** | 2.2.22+ | Industry-standard process mining library |
| **Pandas** | 2.0.0+ | Data manipulation and analysis |
| **SciPy** | 1.11.0+ | Statistical distributions and tests |
| **NumPy** | (via SciPy) | Numerical computing |

#### Simulation
| Package | Version | Purpose |
|---------|---------|---------|
| **SimPy** | 4.1.1+ | Discrete event simulation framework |

#### User Interface
| Package | Version | Purpose |
|---------|---------|---------|
| **Streamlit** | 1.51.0+ | Interactive web dashboard |
| **Pillow** | 10.0.0+ | Image processing for visualizations |

#### Infrastructure
| Package | Version | Purpose |
|---------|---------|---------|
| **Setuptools** | 80.9.0+ | Package building and distribution |
| **deprecation** | 2.1.0+ | Deprecation warning management |

### Algorithm Details

#### Process Discovery: Inductive Miner
- **Algorithm**: Inductive Miner (IM) algorithm
- **Source**: PM4Py implementation
- **Model Output**: Petri Net + Process Tree
- **Complexity**: O(n log n) where n = number of events
- **Key Property**: Guaranteed to find fitting model
- **Quality Metrics**:
  - Fitness: How well does model replay the log?
  - Precision: Does model overfit to the log?
  - Simplicity: Is the model unnecessarily complex?

#### Distribution Fitting
- **Method**: Kolmogorov-Smirnov (KS) test
- **Candidates**: Normal, Lognormal, Exponential
- **Selection**: Highest p-value (best fit)
- **Purpose**: Parameterize activity duration distributions for simulation

#### Simulation: Discrete Event Simulation
- **Engine**: SimPy (DES framework)
- **Execution Model**: Petri Net semantics
- **Time Model**: Continuous time, event-driven
- **Sampling**: Random sampling from fitted distributions
- **Arrival Model**: Poisson process with estimated arrival rate

#### Validation: Alignment-Based
- **Method**: Edit Distance alignment
- **Metrics**:
  - Token-based fitness
  - Alignment cost
  - Distribution similarity (KS test)
- **Granularity**: Per-trace, per-activity, per-variant

#### Healthcare Metrics: ORE Framework
- **Reference**: Souza et al. (2020)
- **Formula**: ORE = Availability × Performance × Quality
- **Components**:
  - Availability = Scheduled Time / Total Time
  - Performance = Used Time / Scheduled Time
  - Quality = Added Value Time / Used Time
- **Loss Categories**: Equipment, setup, scheduling, cancellation, variation

---

## 4. Core Components

### 4.1 LogAnalyzer (log_analyzer.py - 396 LOC)

**Purpose**: Analyze and profile event logs to understand their structure and characteristics

**Key Responsibilities**:
- Load XES files
- Extract log metadata (traces, events, activities)
- Detect attribute keys (case ID, activity, timestamp, resource)
- Calculate statistics (frequencies, variants, durations)
- Determine log domain/profile

**Main Class**:
```python
class LogAnalyzer:
    def analyze(log_path: Path|str) -> LogProfile
```

**Output**:
```python
@dataclass
class LogProfile:
    num_traces: int                      # Total cases
    num_events: int                      # Total events
    num_unique_activities: int           # Unique activity types
    activity_key: str                    # Attribute key for activities
    timestamp_key: str                   # Attribute key for timestamps
    case_id_key: str                     # Attribute key for case IDs
    resource_key: Optional[str]          # Attribute key for resources (if present)
    activity_frequencies: Dict[str, int] # Event counts per activity
    has_resources: bool                  # Whether log includes resources
    has_lifecycle: bool                  # Whether log has lifecycle info
    min_trace_length: int                # Shortest case
    max_trace_length: int                # Longest case
    num_variants: int                    # Distinct event sequences
    most_common_variants: List[tuple]    # Top variants with frequencies
```

**Key Methods**:
- `analyze()`: Main entry point
- `_load_log()`: XES file loading with error handling
- `_extract_metadata()`: Attribute key detection
- `_calculate_statistics()`: Frequency, variant, and duration analysis

**Error Handling**:
- Validates file existence
- Checks for minimum data requirements (≥1 trace, ≥1 event)
- Graceful handling of missing attributes
- Detailed logging of detection process

---

### 4.2 ProcessMiner (process_mining.py - 459 LOC)

**Purpose**: Discover process models from event logs and extract activity statistics

**Key Responsibilities**:
- Mine Petri Nets using Inductive Miner
- Extract activity statistics (durations, resources)
- Fit distributions to activity durations
- Calculate process model quality metrics
- Handle variant filtering to reduce noise

**Main Classes**:
```python
class ProcessMiner:
    def mine_process(log_path: str, variant_filter: float = 0.8) -> ProcessModel

class DistributionFitter:
    def fit(durations: List[float]) -> Dict[str, Any]
```

**Output**:
```python
@dataclass
class ProcessModel:
    petri_net: object                    # PM4Py Petri Net
    initial_marking: object              # PM4Py initial marking
    final_marking: object                # PM4Py final marking
    activities: Dict[str, ActivityStatistics]  # Per-activity stats
    arrival_rate: float                  # Cases/minute
    dispersion_rate: float               # Standard deviation of arrivals
    median_case_duration: float          # Median duration (minutes)
    num_cases: int                       # Total traces in log
    num_variants: int                    # Distinct sequences
    quality_metrics: Dict[str, float]    # {fitness, precision, simplicity}
    resources: Optional[Dict[str, List[str]]]  # Activity → resource list
    process_tree: Optional[object]       # PM4Py ProcessTree
```

**Activity Statistics**:
```python
@dataclass
class ActivityStatistics:
    min_duration: float
    max_duration: float
    mean_duration: float
    median_duration: float
    std_duration: float
    distribution: Dict[str, Any]   # {name, params, p_value}
    frequency: int                 # Number of occurrences
    resources: List[str]          # Associated resources
```

**Distribution Fitting Algorithm**:
```
1. Extract all durations for activity
2. For each distribution (Normal, Lognormal, Exponential):
   a. Fit parameters using scipy.stats
   b. Run Kolmogorov-Smirnov test
   c. Record p-value
3. Select distribution with highest p-value
4. Return: {name, fitted_params, p_value}
```

**Quality Metrics Calculation**:
- **Fitness** (Token-based replay): Does model replay log?
- **Precision** (Alignment-based): Does model avoid overfitting?
- **Simplicity**: Is model unnecessarily complex?

**Key Methods**:
- `mine_process()`: Main entry point
- `_filter_variants()`: Remove infrequent behavior
- `_mine_petri_net()`: Inductive Miner execution
- `_extract_activity_statistics()`: Duration and resource analysis
- `_fit_distributions()`: Distribution selection
- `_calculate_quality_metrics()`: Fitness, precision, simplicity

**Error Handling**:
- Multiple fitness calculation strategies (fallback chain)
- Graceful handling of empty or single-event logs
- Validation of process model integrity
- Distribution fitting failure recovery

---

### 4.3 LogSimulator (simulation.py - 334 LOC)

**Purpose**: Generate realistic synthetic event logs using discrete event simulation

**Key Responsibilities**:
- Execute Petri Net using SimPy
- Simulate process timing using fitted distributions
- Generate synthetic traces and events
- Export to XES and CSV formats
- Support resource assignment

**Main Classes**:
```python
class LogSimulator:
    def __init__(config: SimulationConfig, verbose: bool = True)
    def simulate(process_model: ProcessModel, output_dir: str = ".") -> SimulationResult

class ActivityExecutor:
    def execute(petri_net, marking, transitions, available_resources)
```

**Simulation Configuration**:
```python
@dataclass
class SimulationConfig:
    num_cases: int = 100                           # Cases to generate
    arrival_rate: Optional[float] = None           # Cases/minute (None = auto)
    activity_durations: Optional[Dict[str, float]] = None  # Custom durations
    variant_filter_percentage: float = 0.8         # Keep top X% variants
    random_seed: int = 42                          # For reproducibility
    max_trace_length: int = 1000                   # Safety limit
```

**Output**:
```python
@dataclass
class SimulationResult:
    csv_path: Path                      # CSV export location
    xes_path: Path                      # XES export location
    num_cases_generated: int            # Traces created
    num_events_generated: int           # Events created
    simulation_time: float              # Wall-clock time (seconds)
    timestamp: datetime                 # Execution timestamp
```

**Simulation Algorithm**:
```
1. Initialize SimPy environment
2. For each case (trace):
   a. Create case process
   b. Increment case counter
   c. Wait for arrival interval
   d. Execute Petri Net:
      - Start at initial marking
      - Fire enabled transitions
      - Sample activity duration from distribution
      - Record event (activity, timestamp, resource)
      - Move to next marking
      - Repeat until final marking
   e. Yield events to accumulator
3. Convert events to XES/CSV format
4. Save to output files
5. Return SimulationResult
```

**Key Features**:
- **Petri Net Execution**: Proper semantics for token flow
- **Distribution Sampling**: Uses fitted distributions from mining
- **Resource Assignment**: Randomly selects from original resource pool
- **Arrival Timing**: Respects discovered arrival patterns
- **Seed Management**: Reproducible random number generation
- **Multi-format Output**: Both XES (standard) and CSV (analysis)

**Key Methods**:
- `simulate()`: Main entry point
- `_initialize_simulation()`: Environment setup
- `_create_case()`: Case process generator
- `_execute_activity()`: Activity simulation with timing
- `_fire_transitions()`: Petri Net execution
- `_generate_events()`: Event log generation
- `_export_xes()`: XES format export
- `_export_csv()`: CSV format export

**Error Handling**:
- Validation of configuration parameters
- Detection of negative durations
- Timeout handling for long-running simulations
- Resource availability checking

---

### 4.4 LogValidator (validation.py - 118 LOC)

**Purpose**: Compare synthetic logs against originals using alignment-based metrics

**Key Responsibilities**:
- Load original and simulated logs
- Calculate alignment-based fitness
- Compute distribution similarity
- Assess overall log quality
- Provide detailed comparison metrics

**Main Class**:
```python
class LogValidator:
    def validate(original_log_path: str, simulated_log_path: str) -> ValidationResult
```

**Output**:
```python
@dataclass
class ValidationResult:
    fitness: float                  # 0-1, higher is better
    cost: float                     # alignment cost, lower is better
    similarity_percentage: float    # 0-100%, higher is better
    details: Dict[str, Any]         # Detailed metrics:
                                    # - num_alignments
                                    # - fitness_min/max
                                    # - cost_min/max
                                    # - activity_similarity
                                    # - variant_similarity
                                    # - duration_similarity
```

**Validation Metrics**:
1. **Edit Distance Alignment**: How many edits to transform trace?
2. **Token-based Fitness**: Can model replay simulated log?
3. **Distribution Similarity**: How similar are activity/variant/duration distributions?
4. **Kolmogorov-Smirnov Test**: Statistical distribution comparison

**Key Methods**:
- `validate()`: Main entry point
- `_calculate_alignment()`: Edit distance computation
- `_calculate_fitness()`: Fitness metric
- `_compare_distributions()`: Statistical comparison
- `_aggregate_metrics()`: Overall similarity score

**Error Handling**:
- Validation of log file existence
- Handling of logs with different sizes
- Graceful processing of missing attribute keys
- Robust alignment computation with edge cases

---

### 4.5 ORECalculator (ore_indicators.py - 451 LOC)

**Purpose**: Calculate healthcare-specific Operating Room Effectiveness (ORE) metrics

**Key Responsibilities**:
- Extract time components from event logs
- Calculate ORE indicator and components
- Analyze loss breakdown
- Handle enriched XES attributes
- Support estimation for incomplete data

**Main Class**:
```python
class ORECalculator:
    def __init__(daily_hours: float = 11.5, setup_time_minutes: float = 15.0)
    def calculate_from_log(log_path: str) -> OREMetrics
```

**Output**:
```python
@dataclass
class OREMetrics:
    # Time components (hours)
    total_time_available: float        # TTA
    total_time_scheduled: float        # TTS
    total_time_used: float             # TTU
    total_time_added_value: float      # TTAV

    # ORE Indicators (0-1 or percentage)
    availability: float                # A = TTS/TTA
    performance: float                 # P = TTU/TTS
    quality: float                     # Q = TTAV/TTU
    ore: float                         # ORE = A × P × Q

    # Loss breakdown (hours)
    loss_equipment_failure: float
    loss_setup: float
    loss_not_scheduling: float
    loss_small_shutdowns: float
    loss_surgery_time_variation: float
    loss_cancellations: float
    loss_reinterventions: float

    # Statistics
    num_surgeries_scheduled: int
    num_surgeries_completed: int
    num_surgeries_cancelled: int
    cancellation_rate: float
    cancellation_reasons: Dict[str, int]

    # Data completeness
    data_coverage_status: Dict[str, float]   # % with each attribute
```

**ORE Framework (Souza et al. 2020)**:

The ORE (Operating Room Effectiveness) metric decomposes operational efficiency into three factors:

```
┌─────────────────────────────────────────────────────────────────┐
│  ORE = Availability × Performance × Quality                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Availability (A) = Scheduled Time / Total Time Available       │
│  └─ What % of available hours are scheduled?                   │
│  └─ Loss categories: Equipment failure, not scheduling         │
│                                                                   │
│  Performance (P) = Used Time / Scheduled Time                   │
│  └─ What % of scheduled time is actually used?                │
│  └─ Loss categories: Setup, small shutdowns, cancellations    │
│                                                                   │
│  Quality (Q) = Added Value Time / Used Time                    │
│  └─ What % of used time adds value?                           │
│  └─ Loss categories: Surgery time variation, reinterventions  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Time Component Definitions**:
- **TTA** (Total Time Available): Daily operating hours × number of days
- **TTS** (Total Time Scheduled): Sum of scheduled surgery durations
- **TTU** (Total Time Used): Sum of actual surgery durations
- **TTAV** (Total Time Added Value): TTU - loss from variations

**Loss Categories**:
1. Equipment Failure: Breakdown and unavailability
2. Setup: Instrument/OR preparation (default 15 min/case)
3. Not Scheduling: Unused slots (TTA - TTS)
4. Small Shutdowns: Rapid stoppages
5. Surgery Time Variation: Difference from expected duration
6. Cancellations: Scheduled but not performed
7. Reinterventions: Repeat procedures

**Key Methods**:
- `calculate_from_log()`: Main entry point
- `_load_log_data()`: Event log loading
- `_extract_time_components()`: TTA, TTS, TTU, TTAV extraction
- `_calculate_ore_indicators()`: A, P, Q, ORE computation
- `_calculate_loss_breakdown()`: Loss category analysis
- `_detect_enriched_attributes()`: Enriched XES detection
- `_calculate_cancellation_metrics()`: Cancellation analysis

**Enriched XES Support**:
- `surgery:status`: Completed, Cancelled, Pending
- `surgery:duration_real_minutes`: Actual surgery time
- `surgery:cancellation_reason`: Reason for cancellation
- `surgery:reintervention`: Boolean indicator

**Data Coverage Tracking**:
- Percentage of events with each attribute
- Estimation methods for missing data
- Confidence reporting

**Error Handling**:
- Graceful handling of standard vs. enriched XES
- Estimation of missing operational attributes
- Validation of time values
- Detailed error messages for data quality issues

---

### 4.6 ProcessMiningPipeline (pipeline.py - 402 LOC)

**Purpose**: Unified facade providing high-level orchestration of the complete workflow

**Key Responsibilities**:
- Coordinate all components
- Manage data flow between stages
- Provide convenient entry points
- Handle configuration
- Aggregate results

**Main Class**:
```python
class ProcessMiningPipeline:
    def __init__(verbose: bool = True, daily_hours: float = 11.5,
                 setup_time_minutes: float = 15.0)

    # Individual operations
    def analyze_log(log_path: str) -> LogProfile
    def mine_process(log_path: str, variant_filter: float = 0.8) -> ProcessModel
    def simulate(process_model: ProcessModel, num_cases: int = 100) -> SimulationResult
    def validate(original_log: str, simulated_log: str) -> ValidationResult
    def calculate_ore(log_path: str) -> OREMetrics

    # Complete workflow
    def run_full_pipeline(log_path: str, variant_filter: float = 0.8) -> Dict
```

**Convenience Function**:
```python
def quick_analysis(log_path: str) -> Dict[str, Any]:
    """Execute complete pipeline with single function call"""
```

**Orchestration Flow**:
```
Input: log_path
  ↓
[1] LogAnalyzer.analyze()
  ├─→ LogProfile
  ↓
[2] ProcessMiner.mine_process()
  ├─→ ProcessModel
  ├─→ quality_metrics
  ↓
[3] LogSimulator.simulate()
  ├─→ SimulationResult
  ├─→ simulated_log (XES)
  ↓
[4] LogValidator.validate()
  ├─→ ValidationResult
  ↓
[5] ORECalculator.calculate()
  ├─→ OREMetrics
  ↓
Output: Aggregated results dictionary
```

**Output Dictionary Structure**:
```python
{
    'analysis': LogProfile,
    'process_model': ProcessModel,
    'simulation_result': SimulationResult,
    'validation_result': ValidationResult,
    'ore_metrics': OREMetrics,
    'execution_summary': {
        'total_time': float,
        'stages_completed': int,
        'success': bool
    }
}
```

**Configuration Management**:
- Verbose logging for all stages
- Healthcare parameters (daily_hours, setup_time)
- Default values for simulation
- Customizable output directories

---

### 4.7 Data Models (models.py - 131 LOC)

**Purpose**: Define strongly-typed data structures for data flow

**Key Data Classes**:

1. **SimulationConfig**: Configuration for synthetic log generation
2. **ProcessModel**: Mined process model with statistics
3. **ActivityStatistics**: Per-activity metrics
4. **SimulationResult**: Output of simulation stage
5. **ValidationResult**: Output of validation stage
6. **OREMetrics**: Healthcare-specific metrics

All use Python `@dataclass` decorator for:
- Automatic `__init__`, `__repr__`, `__eq__`
- Type hints and IDE support
- Serialization support (future JSON export)

---

### 4.8 Utilities (utils.py - 208 LOC)

**Purpose**: Common helper functions used across modules

**Key Functions**:
- `sanitize_activity_name(name: str) -> str`: Clean activity names
- `format_duration(seconds: float) -> str`: Human-readable durations
- `ensure_directory(path: Path|str) -> Path`: Directory creation with validation
- `get_logger(name: str)`: Logging configuration
- `load_xes_log(path: str)`: Error-handling XES loading

---

## 5. Features & Capabilities

### Feature 1: Automatic Log Profiling

**What it does**: Automatically analyzes event log structure without manual configuration

**Input**: XES file path

**Output**: LogProfile with detected attributes and statistics

**Example**:
```python
analyzer = LogAnalyzer()
profile = analyzer.analyze("surgical_log.xes")

# Output:
# LogProfile(
#     num_traces=150,
#     num_events=2340,
#     num_unique_activities=12,
#     activity_key='concept:name',
#     timestamp_key='time:timestamp',
#     case_id_key='case:concept:name',
#     resource_key='org:resource',
#     activity_frequencies={'Incision': 148, 'Suturing': 145, ...},
#     has_resources=True,
#     has_lifecycle=False,
#     num_variants=45,
# )
```

**Capabilities**:
- Detects attribute names automatically
- Works with any domain (healthcare, finance, manufacturing)
- Identifies optional attributes (resources, lifecycle)
- Calculates key statistics without configuration
- No manual attribute mapping required

---

### Feature 2: Process Discovery

**What it does**: Discovers process models (Petri Nets and Process Trees) from event logs

**Input**: Event log (XES file)

**Output**: ProcessModel with discovered structure and statistics

**Algorithm**: Inductive Miner
- **Guarantees**: Always finds a fitting model
- **Quality**: Optimizes for simplicity and fitness
- **Complexity**: O(n log n) where n = number of events

**Example**:
```python
miner = ProcessMiner()
model = miner.mine_process("surgical_log.xes", variant_filter=0.8)

# Output includes:
# ProcessModel(
#     petri_net=<PM4Py Petri Net>,
#     activities={
#         'Incision': ActivityStatistics(
#             min_duration=5.2,
#             max_duration=25.1,
#             mean_duration=12.3,
#             distribution={'name': 'lognorm', 'p_value': 0.87},
#             frequency=148,
#         ),
#         ...
#     },
#     quality_metrics={'fitness': 0.92, 'precision': 0.88, 'simplicity': 0.95},
#     arrival_rate=0.15,  # cases/minute
# )
```

**Quality Metrics**:
- **Fitness** (0-1): How well does model replay the log?
- **Precision** (0-1): Does model avoid overfitting?
- **Simplicity** (0-1): Is the model unnecessarily complex?

**Advanced Features**:
- **Variant Filtering**: Removes infrequent behavior (noise)
- **Distribution Fitting**: Identifies best distribution for each activity duration
- **Resource Extraction**: Maps resources to activities
- **Arrival Pattern**: Detects case arrival rates

---

### Feature 3: Synthetic Log Generation

**What it does**: Creates realistic synthetic event logs using discovered process models

**Input**: ProcessModel from discovery phase

**Output**: Synthetic log in XES and CSV formats

**Engine**: Discrete Event Simulation (SimPy)

**Example**:
```python
config = SimulationConfig(
    num_cases=200,
    random_seed=42,  # reproducible
)

simulator = LogSimulator(config)
result = simulator.simulate(model, output_dir="output/")

# Output includes:
# - output/simulated_synthetic.xes (200 synthetic cases)
# - output/simulated_synthetic.csv (6000+ events)
# SimulationResult(
#     num_cases_generated=200,
#     num_events_generated=6234,
#     simulation_time=2.34,  # seconds
# )
```

**Realism Features**:
- **Distribution-based Timing**: Activity durations follow discovered distributions
- **Arrival Patterns**: Case arrivals match original log pattern
- **Resource Assignment**: Randomly selects from original resource pool
- **Variant Distribution**: Follows original variant frequencies
- **Reproducibility**: Seed-based random number generation

**Customization**:
- Number of cases to generate
- Custom arrival rates
- Custom activity durations
- Variant filtering
- Random seed for reproducibility

---

### Feature 4: Log Validation

**What it does**: Compares synthetic logs against originals to assess generation quality

**Input**: Original log path, Simulated log path

**Output**: ValidationResult with quality metrics

**Example**:
```python
validator = LogValidator()
result = validator.validate("original.xes", "synthetic.xes")

# Output:
# ValidationResult(
#     fitness=0.94,                    # 94% fitness
#     cost=12.5,                       # alignment cost
#     similarity_percentage=91.2,      # 91.2% similarity
#     details={
#         'num_alignments': 400,
#         'fitness_min': 0.85,
#         'fitness_max': 0.99,
#         'activity_similarity': 0.92,
#         'variant_similarity': 0.89,
#         'duration_similarity': 0.94,
#     }
# )
```

**Validation Metrics**:
- **Fitness**: Can original model replay synthetic log?
- **Cost**: What's the alignment cost (lower is better)?
- **Similarity**: Overall distribution similarity (KS test)
- **Per-Activity**: Activity frequency comparison
- **Per-Variant**: Process variant distribution comparison
- **Per-Duration**: Activity duration distribution comparison

**Interpretation**:
- **Fitness > 0.9**: Synthetic log well-fits original model
- **Similarity > 0.85**: Synthetic log closely matches original
- **Cost < 5**: Good alignment quality

---

### Feature 5: Healthcare Metrics (ORE)

**What it does**: Calculates Operating Room Effectiveness indicators from surgical logs

**Input**: Event log (preferably enriched with surgical attributes)

**Output**: OREMetrics with efficiency breakdown

**Framework**: Souza et al. (2020) ORE methodology

**Example**:
```python
calc = ORECalculator(
    daily_hours=11.5,      # Operating room open 11.5 hours/day
    setup_time_minutes=15.0 # 15 min setup between cases
)
metrics = calc.calculate_from_log("surgical_log.xes")

# Output:
# OREMetrics(
#     ore=0.687,                          # 68.7% overall effectiveness
#     availability=0.82,                  # 82% of time scheduled
#     performance=0.91,                   # 91% of scheduled time used
#     quality=0.92,                       # 92% of used time adds value
#     num_surgeries_completed=147,
#     num_surgeries_cancelled=3,
#     cancellation_rate=0.02,
#     loss_equipment_failure=2.5,         # hours
#     loss_setup=18.7,
#     loss_not_scheduling=15.2,
#     loss_cancellations=1.3,
# )
```

**Key Insights**:
- **ORE Interpretation**: Percentage of available time that adds value
- **Loss Breakdown**: Where time is wasted (equipment, setup, cancellations, etc.)
- **Bottleneck Identification**: Which loss category is largest?
- **Improvement Targets**: Where to focus optimization efforts

**Enriched XES Support**:
- Extracts `surgery:status` (completed, cancelled)
- Uses `surgery:duration_real_minutes` for actual times
- Analyzes `surgery:cancellation_reason` for root cause
- Tracks reinterventions via `surgery:reintervention`

---

### Feature 6: Web Interface

**What it does**: Interactive Streamlit dashboard for non-technical users

**Location**: `app/app.py`

**Features**:
- **File Upload**: Drag-and-drop XES file upload
- **Two Execution Modes**:
  - "Run Everything": Complete pipeline at once
  - "Step-by-Step": Individual control of each phase
- **Interactive Visualizations**:
  - Petri Net diagram (requires graphviz)
  - Activity frequency bar charts
  - Process variant distribution
  - Quality metrics display
  - Validation result interpretation
- **Downloadable Results**: Export CSV and XES files
- **Date Filtering**: Optional temporal filtering

**User Experience**:
1. Upload XES file
2. Choose execution mode
3. View progress indicators
4. Inspect results
5. Download outputs
6. View recommendations

---

## 6. Data Flow & Workflow

### Complete Workflow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│                    USER INPUT: log.xes                            │
│                                                                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │   STAGE 1: LOG ANALYSIS                │
        │   LogAnalyzer.analyze(log.xes)         │
        └────────┬───────────────────────────────┘
                 │
                 ├─→ Load XES file
                 ├─→ Extract traces and events
                 ├─→ Detect attribute keys
                 │  └─→ activity_key, timestamp_key, case_id_key, resource_key
                 ├─→ Count entities
                 │  └─→ traces, events, unique activities, variants
                 ├─→ Calculate statistics
                 │  └─→ frequencies, trace lengths, variant distributions
                 ├─→ Detect resources
                 │
                 ▼
            ┌─────────────────┐
            │  LogProfile     │
            │  (Metadata)     │
            └────────┬────────┘
                     │
                     ▼
        ┌────────────────────────────────────────┐
        │   STAGE 2: PROCESS MINING              │
        │   ProcessMiner.mine_process(log.xes)   │
        └────────┬───────────────────────────────┘
                 │
                 ├─→ Apply variant filtering (keep top X%)
                 │
                 ├─→ Discover Petri Net
                 │  └─→ Using Inductive Miner algorithm
                 │
                 ├─→ Discover Process Tree
                 │
                 ├─→ Extract Activity Statistics
                 │  ├─→ Duration distribution fitting
                 │  │  └─→ Try: Normal → Lognormal → Exponential
                 │  │  └─→ Select via KS test (highest p-value)
                 │  ├─→ Resource mapping
                 │  └─→ Frequency counts
                 │
                 ├─→ Calculate Arrival Rates
                 │  └─→ Poisson process parameter estimation
                 │
                 ├─→ Evaluate Model Quality
                 │  ├─→ Fitness (token-based replay)
                 │  ├─→ Precision (alignment-based)
                 │  └─→ Simplicity (structure analysis)
                 │
                 ▼
            ┌──────────────────┐
            │  ProcessModel    │
            │  - Petri Net     │
            │  - Statistics    │
            │  - Quality       │
            │    Metrics       │
            └────────┬─────────┘
                     │
                     ▼
        ┌────────────────────────────────────────┐
        │   STAGE 3: SIMULATION                  │
        │   LogSimulator.simulate(process_model) │
        └────────┬───────────────────────────────┘
                 │
                 ├─→ Initialize SimPy environment
                 │
                 ├─→ For each case (0 to N):
                 │  ├─→ Generate case ID
                 │  ├─→ Sample arrival time
                 │  ├─→ Execute Petri Net:
                 │  │  ├─→ Start at initial marking
                 │  │  ├─→ Fire enabled transitions
                 │  │  ├─→ For each transition (activity):
                 │  │  │  ├─→ Sample duration from distribution
                 │  │  │  ├─→ Sample resource from pool
                 │  │  │  ├─→ Record event
                 │  │  │  └─→ Yield control to SimPy
                 │  │  ├─→ Continue until final marking
                 │  │  └─→ Mark case complete
                 │
                 ├─→ Aggregate events
                 │
                 ├─→ Export to XES format
                 │  └─→ Convert events to XES structure
                 │
                 ├─→ Export to CSV format
                 │  └─→ Create tabular representation
                 │
                 ▼
            ┌───────────────────┐
            │  SimulationResult │
            │  - XES file       │
            │  - CSV file       │
            │  - Statistics     │
            └────────┬──────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │   STAGE 4: VALIDATION                                     │
    │   LogValidator.validate(original.xes, simulated.xes)     │
    └────────┬─────────────────────────────────────────────────┘
             │
             ├─→ Load both logs
             │
             ├─→ For each trace:
             │  ├─→ Calculate edit distance alignment
             │  ├─→ Compute fitness
             │  └─→ Record cost
             │
             ├─→ Extract feature distributions:
             │  ├─→ Activity frequencies
             │  ├─→ Variant frequencies
             │  └─→ Duration distributions
             │
             ├─→ Compare distributions (KS test)
             │
             ├─→ Aggregate metrics
             │
             ▼
        ┌─────────────────────┐
        │  ValidationResult   │
        │  - Fitness          │
        │  - Similarity %     │
        │  - Cost             │
        │  - Details          │
        └────────┬────────────┘
                 │
        ┌────────┴──────────────────────────────────────────────┐
        │                                                        │
        ▼                                                        ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │   STAGE 5: ORE CALCULATION (Healthcare)                         │
    │   ORECalculator.calculate_from_log(original.xes)               │
    └────────┬────────────────────────────────────────────────────────┘
             │
             ├─→ Convert log to DataFrame
             │
             ├─→ Detect enriched XES attributes
             │  ├─→ surgery:status
             │  ├─→ surgery:duration_real_minutes
             │  └─→ surgery:cancellation_reason
             │
             ├─→ Extract time components:
             │  ├─→ TTA = daily_hours × num_days
             │  ├─→ TTS = sum(scheduled durations)
             │  ├─→ TTU = sum(actual durations)
             │  └─→ TTAV = TTU - losses
             │
             ├─→ Decompose losses:
             │  ├─→ Equipment failure
             │  ├─→ Setup time
             │  ├─→ Not scheduled
             │  ├─→ Small shutdowns
             │  ├─→ Surgery time variation
             │  ├─→ Cancellations
             │  └─→ Reinterventions
             │
             ├─→ Calculate ORE indicators:
             │  ├─→ A (Availability) = TTS / TTA
             │  ├─→ P (Performance) = TTU / TTS
             │  ├─→ Q (Quality) = TTAV / TTU
             │  └─→ ORE = A × P × Q
             │
             ├─→ Analyze cancellations
             │  ├─→ Cancellation rate
             │  └─→ Reason breakdown
             │
             ▼
        ┌──────────────────┐
        │   OREMetrics     │
        │   - ORE %        │
        │   - Components   │
        │   - Loss Detail  │
        │   - Cancellations
        └────────┬─────────┘
                 │
                 ▼
    ┌─────────────────────────────────────────┐
    │   OUTPUT: Results Dictionary            │
    │   {                                     │
    │     'analysis': LogProfile,             │
    │     'process_model': ProcessModel,      │
    │     'simulation_result': SimResult,     │
    │     'validation_result': ValResult,     │
    │     'ore_metrics': OREMetrics           │
    │   }                                     │
    └─────────────────────────────────────────┘
```

### Data Structure Transformations

**1. XES File → Event Log (in-memory)**
```
XES (XML format)
├─ Trace 1
│  ├─ Event 1: {attributes}
│  ├─ Event 2: {attributes}
│  └─ Event 3: {attributes}
└─ Trace 2
   └─ ...

↓ (Via PM4Py XES importer)

EventLog (Python object)
├─ Trace 1: [Event, Event, Event]
├─ Trace 2: [Event, Event, ...]
└─ ...
```

**2. EventLog → DataFrame (for analysis)**
```
EventLog
↓
DataFrame Rows:
│ Index │ case_id │ activity    │ timestamp      │ duration │ resource │
├───────┼─────────┼─────────────┼────────────────┼──────────┼──────────┤
│ 0     │ 001     │ Incision    │ 2023-01-01... │ 15.2     │ Doctor1  │
│ 1     │ 001     │ Suturing    │ 2023-01-01... │ 8.5      │ Doctor1  │
│ 2     │ 002     │ Incision    │ 2023-01-01... │ 12.1     │ Doctor2  │
└───────┴─────────┴─────────────┴────────────────┴──────────┴──────────┘
```

**3. Durations → Distribution Parameters**
```
[15.2, 14.8, 15.5, 14.9, 15.1, 14.7, 15.3, ...]
↓ (scipy.stats fitting)
Candidate distributions:
  - Normal: μ=15.05, σ=0.28, p-value=0.45
  - Lognormal: shape=0.019, loc=15.05, scale=0.19, p-value=0.89 ← BEST
  - Exponential: scale=15.05, p-value=0.12
↓ (Select highest p-value)
Use for simulation: np.random.lognormal(...)
```

**4. ProcessModel → Synthetic Events (via Simulation)**
```
ProcessModel (Petri Net + Statistics)
↓
SimPy Simulation Loop:
  For i in 1..N_cases:
    arrival_time = sample_arrival()
    trace = []
    marking = initial_marking
    while marking != final_marking:
      transition = select_enabled_transition()
      duration = sample_distribution(transition.activity)
      resource = random.choice(available_resources)
      event = Event(case=i, activity, timestamp, duration, resource)
      trace.append(event)
      marking = fire(transition, marking)
    yield trace
↓
Synthetic Events: [Case1: [Event...], Case2: [Event...], ...]
↓
Export → XES / CSV
```

---

## 7. Module Reference

### Quick Module Lookup

| Module | LOC | Main Classes | Key Functions |
|--------|-----|--------------|----------------|
| `log_analyzer.py` | 396 | LogAnalyzer, LogProfile | analyze() |
| `process_mining.py` | 459 | ProcessMiner, DistributionFitter, ActivityStatistics | mine_process(), fit() |
| `simulation.py` | 334 | LogSimulator, ActivityExecutor | simulate() |
| `validation.py` | 118 | LogValidator, ValidationResult | validate() |
| `ore_indicators.py` | 451 | ORECalculator, OREMetrics | calculate_from_log() |
| `pipeline.py` | 402 | ProcessMiningPipeline | run_full_pipeline(), quick_analysis() |
| `models.py` | 131 | 6 dataclasses | (Data structure definitions) |
| `utils.py` | 208 | (Helper module) | sanitize_activity_name(), format_duration() |

### Module Dependencies

```
pipeline.py
├─→ log_analyzer.py
├─→ process_mining.py
├─→ simulation.py
├─→ validation.py
├─→ ore_indicators.py
└─→ models.py

process_mining.py
├─→ models.py
├─→ utils.py
└─→ (PM4Py, SciPy)

simulation.py
├─→ models.py
├─→ utils.py
└─→ (SimPy, PM4Py, Pandas)

ore_indicators.py
├─→ models.py
├─→ utils.py
└─→ (Pandas, SciPy)

validation.py
├─→ models.py
└─→ (PM4Py, Pandas)

log_analyzer.py
├─→ models.py
└─→ (PM4Py, Pandas)

app/app.py
└─→ pipeline.py
    └─→ (All components)
```

---

## 8. APIs & Interfaces

### Public API

The primary public interface is the `ProcessMiningPipeline` facade:

```python
from pipeline import ProcessMiningPipeline, quick_analysis

# High-level convenience
results = quick_analysis("log.xes")

# More control
pipeline = ProcessMiningPipeline(verbose=True)
log_profile = pipeline.analyze_log("log.xes")
process_model = pipeline.mine_process("log.xes")
sim_result = pipeline.simulate(process_model, num_cases=100)
validation = pipeline.validate("original.xes", "synthetic.xes")
ore = pipeline.calculate_ore("log.xes")

# Complete pipeline
full_results = pipeline.run_full_pipeline("log.xes")
```

### Component-Level APIs

Each component can be imported and used independently:

```python
from log_analyzer import LogAnalyzer
from process_mining import ProcessMiner
from simulation import LogSimulator, SimulationConfig
from validation import LogValidator
from ore_indicators import ORECalculator
```

### Data Structure APIs

```python
from models import (
    ProcessModel,
    ActivityStatistics,
    SimulationConfig,
    SimulationResult,
    ValidationResult,
    OREMetrics
)
```

---

## 9. Configuration & Deployment

### Installation

```bash
# Clone repository
git clone https://github.com/viniciusbregoli/Sim2Log-core.git
cd Sim2Log-core

# Install dependencies
pip install -e .

# For web UI
pip install -r app/requirements.txt
```

### Dependencies

```toml
setuptools>=80.9.0
simpy>=4.1.1
streamlit>=1.51.0
pandas>=2.0.0
scipy>=1.11.0
pm4py>=2.2.22
deprecation>=2.1.0
Pillow>=10.0.0
```

### Running the Web Interface

```bash
streamlit run app/app.py
```

Default: Opens at http://localhost:8501

### Command-Line Usage

```python
# Using quick_analysis convenience function
python -c "
from pipeline import quick_analysis
results = quick_analysis('path/to/log.xes')
print(results.keys())
"

# Using ProcessMiningPipeline
python -c "
from pipeline import ProcessMiningPipeline
pipeline = ProcessMiningPipeline()
profile = pipeline.analyze_log('log.xes')
print(f'Log has {profile.num_traces} cases and {profile.num_events} events')
"
```

### Environment Variables

Currently none required. Configuration is done via code parameters or Streamlit sidebar.

### File Paths

- **Input**: Accepts absolute/relative paths to XES files
- **Output**: Creates `outputs/` directory (if using pipeline directly)
- **Web UI**: `app/uploads/` (inputs), `app/outputs/` (results)

---

## 10. Testing & Quality Assurance

### Testing Approach

The project uses integration testing combined with debug scripts:

### Test Files

**1. test.py - Integration Test**
```bash
python test.py path/to/log.xes [--num-cases N]
```

Tests complete workflow:
1. Mine process model
2. Generate N synthetic cases
3. Validate synthetic log
4. Display metrics

**2. test_mining_metrics.py - Metrics Debug**
```bash
python test_mining_metrics.py path/to/log.xes
```

Debugs quality metric calculations

### Quality Metrics

| Metric | Typical Range | Interpretation |
|--------|---------------|-----------------|
| Fitness | 0.8-1.0 | How well model replays log |
| Precision | 0.85-1.0 | Model avoids overfitting |
| Simplicity | 0.9-1.0 | Model complexity |
| Similarity | 85%-100% | Synthetic vs. original match |

### Test Coverage

- **Log Loading**: XES parsing, error handling
- **Process Discovery**: Petri Net mining, quality metrics
- **Simulation**: Event generation, formatting
- **Validation**: Fitness, alignment, distributions
- **ORE Calculation**: Time component extraction, metric computation

---

## 11. Research Contributions

### Key Innovation Areas

1. **Unified Pipeline**: Combines mining, simulation, validation in single system
2. **Enriched XES Support**: Custom attributes for operational data
3. **Distribution-Aware Simulation**: Uses fitted distributions for realism
4. **Healthcare Focus**: ORE metrics adapted for surgical analytics
5. **Quality Assurance**: Multiple validation metrics for synthetic logs

### Novel Aspects

- **Integrated Validation**: Multi-level comparison (fitness, alignment, distributions)
- **Automatic Log Profiling**: Domain-agnostic attribute detection
- **Reproducible Simulation**: Seed-based deterministic generation
- **Loss Decomposition**: ORE framework with detailed loss categories

### Potential Research Extensions

- Machine learning for parameter optimization
- Multi-process log support
- Real-time simulation monitoring
- Advanced visualization of process models
- Predictive analytics based on simulated scenarios
- Resource-constrained simulation
- Cost-aware process simulation

---

## 12. Future Directions

### Planned Enhancements

1. **Advanced Analytics**
   - Predictive models for duration estimation
   - Anomaly detection in process executions
   - Resource utilization optimization
   - Schedule optimization based on ORE

2. **Extended Data Support**
   - Support for multiple input formats (CSV, JSON, SQL)
   - Real-time event stream processing
   - Incremental log analysis and updates

3. **Improved Visualization**
   - Interactive Petri Net visualization
   - Process animation with synthetic events
   - Real-time ORE dashboard
   - Resource utilization heatmaps

4. **Performance Optimization**
   - Parallel processing for large logs
   - Incremental model updates
   - Distributed simulation

5. **Cloud Deployment**
   - Docker containerization
   - Cloud-based API service
   - Multi-tenant support

---

## Summary

**Sim2Log-Core** is a comprehensive, modular framework for process mining and simulation with healthcare-specific enhancements. The architecture balances simplicity (unified facade) with flexibility (component-level APIs), making it suitable for both researchers and practitioners.

The framework demonstrates best practices in software engineering:
- Clear separation of concerns
- Modular, reusable components
- Type-safe data structures
- Comprehensive error handling
- Multi-interface design (API + UI)
- Reproducible results
- Extensive documentation

For thesis work, emphasize the **unified approach** to the complete process mining workflow, the **domain-agnostic design** with healthcare specialization, and the **quality assurance mechanisms** for synthetic log validation.

---

**Document Generated**: 2025-11-17
**Framework Version**: 0.1.0
**For**: Academic thesis and research documentation
