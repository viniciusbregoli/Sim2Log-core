ORE Indicators - Effectiveness Metrics
=======================================

.. currentmodule:: ore_indicators

The :class:`ORECalculator` computes Operating Room Effectiveness (or any process effectiveness) metrics.

ORECalculator
-------------

.. autoclass:: ORECalculator
   :members:
   :undoc-members:
   :show-inheritance:

OREMetrics
----------

.. autoclass:: OREMetrics
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

Basic Calculation
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from ore_indicators import ORECalculator

   # Create calculator
   calculator = ORECalculator(
       verbose=True,
       daily_hours=11.5,      # Operating hours per day
       setup_time_minutes=15  # Setup time between activities
   )

   # Calculate ORE from log
   metrics = calculator.calculate_from_log("enriched_log.xes")

   # Access ORE metrics
   print(f"ORE: {metrics.ore:.1f}%")
   print(f"  Availability: {metrics.availability:.1f}%")
   print(f"  Performance: {metrics.performance:.1f}%")
   print(f"  Quality: {metrics.quality:.1f}%")

   # Access time breakdown
   print(f"\nTime Budget:")
   print(f"  Available: {metrics.total_time_available:.1f}h")
   print(f"  Scheduled: {metrics.total_time_scheduled:.1f}h")
   print(f"  Used: {metrics.total_time_used:.1f}h")
   print(f"  Added Value: {metrics.total_time_added_value:.1f}h")

   # Access loss breakdown
   print(f"\nLosses:")
   print(f"  Setup: {metrics.loss_setup:.1f}h")
   print(f"  Not Scheduling: {metrics.loss_not_scheduling:.1f}h")
   print(f"  Cancellations: {metrics.loss_cancellations:.1f}h")
   print(f"  Time Variation: {metrics.loss_surgery_time_variation:.1f}h")

   # Access surgery statistics
   print(f"\nSurgeries:")
   print(f"  Scheduled: {metrics.num_surgeries_scheduled}")
   print(f"  Completed: {metrics.num_surgeries_completed}")
   print(f"  Cancelled: {metrics.num_surgeries_cancelled} ({metrics.cancellation_rate:.1f}%)")

Improvement Scenarios
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from ore_indicators import calculate_ore_scenarios
   import pandas as pd

   # Calculate baseline
   metrics = calculator.calculate_from_log("log.xes")

   # Generate improvement scenarios
   scenarios_df = calculate_ore_scenarios(metrics)

   # Display scenarios
   print(scenarios_df)

   # Example output:
   # Scenario A: No scheduling = 0 → ORE increases to 45%
   # Scenario B: 5 min reduction in setup → ORE increases to 42%
   # Scenario G: Combined improvements → ORE increases to 50%

Using Enriched XES
^^^^^^^^^^^^^^^^^^

For better accuracy, use enriched XES files with operational data:

.. code-block:: bash

   # Convert Excel to enriched XES
   uv run python converters/convert_xlsx_to_xes.py surgery_data.xlsx enriched_log.xes

.. code-block:: python

   # Calculate ORE with real data
   metrics = calculator.calculate_from_log("enriched_log.xes")

   # Real data fields used:
   # - surgery:status (Realizada/Cancelada/Interrompida)
   # - surgery:duration_real_minutes (actual duration)
   # - surgery:cancellation_reason (why cancelled)
