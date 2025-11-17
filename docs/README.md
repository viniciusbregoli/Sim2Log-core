# Sim2Log Documentation

This directory contains the Sphinx documentation for Sim2Log.

## Building Documentation

### Prerequisites

Install Sphinx and theme:

```bash
uv pip install sphinx sphinx-rtd-theme
```

### Build HTML Documentation

```bash
./build_docs.sh
```

Or manually:

```bash
cd docs
sphinx-build -b html source build/html
```

### View Documentation

Open `build/html/index.html` in your browser.

## Documentation Structure

```
docs/
├── source/
│   ├── conf.py                 # Sphinx configuration
│   ├── index.rst               # Main page
│   ├── quickstart.rst          # Quick start guide
│   ├── modules.rst             # Modules overview
│   ├── examples.rst            # Usage examples
│   ├── enriched_xes.rst        # Enriched XES format
│   ├── changelog.rst           # Version history
│   ├── contributing.rst        # Contribution guidelines
│   └── api/                    # API reference
│       ├── pipeline.rst
│       ├── log_analyzer.rst
│       ├── process_mining.rst
│       ├── simulation.rst
│       ├── validation.rst
│       ├── ore_indicators.rst
│       └── models.rst
├── build/                      # Generated HTML (ignored by git)
├── build_docs.sh               # Build script
└── README.md                   # This file
```

## Auto-Generated API Documentation

The API documentation is automatically generated from docstrings using Sphinx's `autodoc` extension with Napoleon for Google-style docstrings.

## Adding New Documentation

1. Create `.rst` file in `source/`
2. Add to `index.rst` toctree
3. Rebuild documentation

Example:

```rst
My New Page
===========

Content here...

.. code-block:: python

   # Code example
   from pipeline import ProcessMiningPipeline
   pipeline = ProcessMiningPipeline()
```

## Documentation Style Guide

- Use Google-style docstrings in code
- Include code examples in docstrings
- Cross-reference with `:class:`, `:func:`, `:mod:`
- Add examples for all public APIs
- Keep language clear and concise
