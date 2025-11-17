Contributing
============

We welcome contributions to Sim2Log!

Development Setup
-----------------

1. Clone repository
2. Install with development dependencies:

.. code-block:: bash

   cd core
   uv pip install -e ".[dev]"

3. Run tests:

.. code-block:: bash

   uv run pytest

Code Style
----------

- Follow PEP 8
- Use type hints
- Write Google-style docstrings
- Keep modules independent

Documentation
-------------

To build documentation locally:

.. code-block:: bash

   cd docs
   ./build_docs.sh

Documentation uses Sphinx with the Read the Docs theme.

Adding New Modules
------------------

When adding a new module:

1. Create class with comprehensive docstring
2. Add to ``__init__.py`` exports
3. Create API documentation in ``docs/source/api/``
4. Add examples to ``docs/source/examples.rst``
5. Update ``docs/source/modules.rst``

Docstring Template
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class MyModule:
       """
       Brief description of the module.

       More detailed explanation of what it does and when to use it.

       Attributes:
           attr1 (type): Description
           attr2 (type): Description

       Example:
           >>> module = MyModule()
           >>> result = module.process("input.xes")
           >>> print(result.summary)
       """

       def __init__(self, param1: str, param2: int = 10):
           """
           Initialize module.

           Args:
               param1: Description of param1
               param2: Description of param2, defaults to 10

           Example:
               >>> module = MyModule("config", param2=20)
           """
           pass

       def process(self, input_path: Path) -> Result:
           """
           Process input file.

           Args:
               input_path: Path to input file

           Returns:
               Result object with processed data

           Raises:
               FileNotFoundError: If input file doesn't exist
               ValueError: If input is invalid

           Example:
               >>> result = module.process("data.xes")
               >>> print(result.num_cases)
           """
           pass

Testing
-------

Write tests for new functionality:

.. code-block:: python

   def test_my_module():
       module = MyModule("config")
       result = module.process("test_data.xes")
       assert result.num_cases > 0

Contact
-------

- GitHub Issues: https://github.com/yourusername/sim2log/issues
- Email: your.email@example.com
