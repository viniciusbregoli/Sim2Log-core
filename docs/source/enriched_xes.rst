Enriched XES Format
===================

Sim2Log supports **enriched XES files** with custom operational attributes for improved ORE calculation accuracy.

What is Enriched XES?
----------------------

Standard XES files contain:

- Case ID
- Activity names
- Timestamps
- Resources (optional)

**Enriched XES** adds surgical/operational data as custom trace attributes:

- ``surgery:status`` - Surgery status (Realizada/Cancelada/Interrompida)
- ``surgery:duration_real_minutes`` - Actual duration
- ``surgery:cancellation_reason`` - Why cancelled
- ``surgery:scheduled_date`` - When scheduled

Benefits
--------

**Without enriched data (standard XES)**:

- Cancellations estimated from event count (<3 events = cancelled)
- Losses estimated using fixed percentages (6% not-scheduling, 3% variation)
- No cancellation reasons

**With enriched data**:

- ✅ **Real cancellation count**: 256 surgeries (18%) from ``surgery:status``
- ✅ **Real duration data**: 81.3% coverage from ``surgery:duration_real_minutes``
- ✅ **Cancellation reasons**: Tracked from ``surgery:cancellation_reason``
- ✅ **More accurate ORE**: Based on actual operational data

Converting Excel to Enriched XES
---------------------------------

Use the provided converter:

.. code-block:: bash

   cd core
   uv run python converters/convert_xlsx_to_xes.py \
       bases/CirurgiasMarcoHuc.xlsx \
       bases/xes/CirurgiasMarcoHucEnriched.xes

Expected output:

.. code-block:: text

   Reading bases/CirurgiasMarcoHuc.xlsx...
   Processing 1421 cases...

   Conversion Summary:
     Total traces: 1419
     Total events: 10827

   Operational Data Coverage:
     Traces with status: 1419
     Traces with actual duration: 1154
     Traces cancelled: 256
     Traces with cancellation reason: 256

   Conversion complete!

Excel File Requirements
-----------------------

The Excel file should have these columns:

**Required**:

- ``NR_CIRURGIA`` - Case ID
- ``DT_INICIO`` - Start date
- ``ENTRADA_SALA``, ``INICIO_PROC_CIRURGICO``, etc. - Event timestamps
- ``SALA`` - Room
- ``DS_PROCEDIMENTO`` - Procedure name

**Optional (for enriched data)**:

- ``DS_STATUS_CIRURGIA`` - Status (Realizada/Cancelada/Interrompida)
- ``NR_MIN_DURACAO_REAL`` - Actual duration in minutes
- ``DS_MOTIVO_CANCEL`` - Cancellation reason

Using Enriched XES
------------------

Enriched XES works seamlessly with all modules:

**Process Mining**:

.. code-block:: python

   from process_mining import ProcessMiner

   miner = ProcessMiner()
   model = miner.mine_process("enriched_log.xes", variant_filter=0.8)

   # Works normally - includes cancelled surgeries as single-event traces
   print(f"Total cases: {model.num_cases}")  # 1,419 (includes 256 cancelled)

**ORE Calculation** (automatically uses real data):

.. code-block:: python

   from ore_indicators import ORECalculator

   calc = ORECalculator(verbose=True)
   metrics = calc.calculate_from_log("enriched_log.xes")

   # Output shows:
   # [ORECalculator] Data Coverage:
   # [ORECalculator]   With status: 1419 (100.0%)
   # [ORECalculator]   With real duration: 1154 (81.3%)
   # [ORECalculator]   With cancellation reason: 256
   # [ORECalculator] Cancellations: 256 surgeries cancelled (REAL DATA)

   print(f"Real cancellations: {metrics.num_surgeries_cancelled}")
   print(f"Cancellation rate: {metrics.cancellation_rate:.1f}%")

Custom Extension
----------------

The enriched format uses a custom XES extension:

.. code-block:: xml

   <extension name="Surgical" prefix="surgery"
              uri="http://custom.org/surgery.xesext"/>

This allows any XES-compliant tool to read the file while preserving custom data.

Creating Your Own Enriched XES
-------------------------------

To add custom operational data to your XES files:

1. **Add extension** to log header:

.. code-block:: python

   from xml.etree import ElementTree as ET

   log = ET.Element('log', {
       'xes.version': '1849-2016',
       'xmlns': 'http://www.xes-standard.org/'
   })

   ET.SubElement(log, 'extension', {
       'name': 'MyDomain',
       'prefix': 'custom',
       'uri': 'http://example.org/custom.xesext'
   })

2. **Add trace attributes**:

.. code-block:: python

   trace = ET.SubElement(log, 'trace')

   # Standard attribute
   ET.SubElement(trace, 'string', {
       'key': 'concept:name',
       'value': 'CASE_001'
   })

   # Custom attribute
   ET.SubElement(trace, 'string', {
       'key': 'custom:status',
       'value': 'Completed'
   })

   ET.SubElement(trace, 'float', {
       'key': 'custom:actual_duration',
       'value': '125.5'
   })

3. **Read custom attributes** in your code:

.. code-block:: python

   from pm4py.objects.log.importer.xes import importer as xes_importer

   log = xes_importer.apply("enriched.xes")

   for trace in log:
       status = trace.attributes.get('custom:status')
       duration = trace.attributes.get('custom:actual_duration')
       print(f"Status: {status}, Duration: {duration}")

Validation
----------

Verify enriched XES format:

.. code-block:: python

   from log_analyzer import LogAnalyzer

   analyzer = LogAnalyzer()
   profile = analyzer.analyze("enriched_log.xes")

   # Check if enrichment was successful
   print(f"Traces: {profile.num_traces}")
   print(f"Events: {profile.num_events}")
   print(f"Min trace length: {profile.min_trace_length}")  # Should be 1 for cancelled

   # Cancelled surgeries have exactly 1 event
   if profile.min_trace_length == 1:
       print("✓ Enriched XES includes cancelled cases")
