Validation - Log Comparison
============================

.. currentmodule:: validation

The :class:`LogValidator` compares original and synthetic logs to measure quality.

LogValidator
------------

.. autoclass:: LogValidator
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

   from validation import LogValidator

   # Create validator
   validator = LogValidator(verbose=True)

   # Validate synthetic log
   result = validator.validate(
       "original_log.xes",
       "simulated_log.xes"
   )

   # Access validation results
   print(f"Overall similarity: {result.similarity_percentage:.1f}%")
   print(f"Activity distribution: {result.activity_distribution_similarity:.3f}")
   print(f"Variant distribution: {result.variant_distribution_similarity:.3f}")
   print(f"Duration distribution: {result.duration_distribution_similarity:.3f}")

   # Check statistical test
   print(f"KS test p-value: {result.statistical_test_p_value:.4f}")
   if result.statistical_test_p_value > 0.05:
       print("Distributions are statistically similar ✓")
   else:
       print("Distributions differ significantly ✗")

   # Access detailed statistics
   details = result.details
   print(f"Original cases: {details['original_num_traces']}")
   print(f"Simulated cases: {details['synthetic_num_traces']}")
