Log Analyzer - Profile Detection
==================================

.. currentmodule:: log_analyzer

The :class:`LogAnalyzer` detects log characteristics automatically.

LogAnalyzer
-----------

.. autoclass:: LogAnalyzer
   :members:
   :undoc-members:
   :show-inheritance:

LogProfile
----------

.. autoclass:: LogProfile
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

   from log_analyzer import LogAnalyzer

   # Create analyzer
   analyzer = LogAnalyzer(verbose=True)

   # Analyze log
   profile = analyzer.analyze("mylog.xes")

   # Access detected characteristics
   print(f"Cases: {profile.num_traces}")
   print(f"Events: {profile.num_events}")
   print(f"Activities: {profile.num_unique_activities}")
   print(f"Variants: {profile.num_variants}")
   print(f"Has resources: {profile.has_resources}")
   print(f"Has timestamps: {profile.timestamp_key is not None}")

   # Check compatibility
   is_compatible, warnings = analyzer.validate_compatibility(profile)
   if not is_compatible:
       for warning in warnings:
           print(f"Warning: {warning}")
