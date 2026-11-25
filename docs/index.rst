metafor-py: selected native Python methods for meta-analysis
============================================================

``metafor-py`` is an experimental Python port of selected methods from Wolfgang Viechtbauer's R package `metafor <https://www.metafor-project.org/>`_. It is a separate implementation, not the R package or a complete replacement. The compatibility table records the scope by function and option.

The project follows the R package's question-to-analysis path: calculate study effects, fit a model, interpret uncertainty, and inspect plots. Its core uses native Python arrays and structured results; optional table inputs use pandas and Patsy.

The tutorials below use pinned R reference inputs shared with Metafor.jl. The wording and plots are original. Local comparison pages show R, Python, and Julia estimates side by side.

Start with the `BCG effect-size tutorial <examples/bcg-effects.html>`_, then follow 21 focused topic pages from model fitting and meta-regression through intervals and forest-plot data. Continue with correlated effects, nested effects, two outcomes, and the supplied-correlation phylogenetic cases. Each page includes a runnable command and interpretation.

To try the package from a checkout, run ``python -m pip install -e '.[tables]'`` from the repository root. The core examples need Python and NumPy; the table and formula adapter uses optional pandas and Patsy dependencies.

Choose a starting point
-----------------------

* To analyze two-group counts, start with `BCG effect sizes <examples/bcg-effects.html>`_.
* To model dependent outcomes, see `correlated sampling errors <examples/dependent-gls.html>`_.
* To use a species correlation matrix, see the `phylogenetic model <examples/phylogeny.html>`_.
* To check formula and matrix rows, see the `table adapter <examples/table-adapter.html>`_.

Compare R, Python, and Julia for the `BCG model <_static/comparisons/bcg-comparison.html>`_, `dependent effects <_static/comparisons/dependent-comparison.html>`_, `phylogenetic models <_static/comparisons/phylogeny-comparison.html>`_, and `effect sizes <_static/comparisons/effect-size-comparison.html>`_. A separate `table-adapter comparison <_static/comparisons/table-adapter-comparison.html>`_ checks Python and Julia row alignment and numeric design matrices. See also the `Metafor.jl documentation <https://itchyshin.github.io/Metafor.jl/>`_ and `Julia source repository <https://github.com/itchyshin/Metafor.jl>`_.

.. note::

   This is an experimental, unreleased port. A passing example establishes parity only for its named fixture, options, and outputs.

What is implemented
-------------------

* Log risk ratios from 2×2 counts, fixed-effect and REML models, and a latitude moderator.
* Mean and new-study prediction intervals, row-aligned forest data, and an original SVG.
* Supplied sampling covariance, nested scalar random effects, two-outcome covariance, and supplied phylogenetic correlation.
* Versioned R reference fixtures. The Python and Julia ports run without R.

The package does not yet implement the full R API. See :download:`the compatibility table <../COMPATIBILITY.md>` for verified, partial, unsupported, and intentional differences.

Project-intended maintainers are Shinichi Nakagawa, Yefeng Yang, and Wolfgang Viechtbauer. This records the intended project team; it does not imply that anyone has accepted a role.

The upstream R project is at `metafor-project.org <https://www.metafor-project.org/>`_; its manuals and function references are at `wviechtb.github.io/metafor <https://wviechtb.github.io/metafor/>`_.

The `metafor-py source repository <https://github.com/itchyshin/metafor-py>`_ contains the implementation, tests, fixtures, and this site's source.

.. toctree::
   :maxdepth: 2

   bcg
   dependent
   examples/index
