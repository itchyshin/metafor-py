metafor-py
==========

**Selected meta-analysis methods, implemented natively in Python.**

``metafor-py`` is an experimental, independently developed port of selected
methods from the R package `metafor <https://www.metafor-project.org/>`_. It
uses Python arrays and results; it is not the R package and does not reproduce
its full API. The `compatibility table <https://github.com/itchyshin/metafor-py/blob/main/COMPATIBILITY.md>`_
records the scope and limits by function and option.

Choose a starting point
-----------------------

* :doc:`Get started <getting-started>` to install the package and run the BCG
  example, from counts to a forest plot.
* Browse the :doc:`reference <reference/index>` for effect sizes, model fits,
  predictions, and covariance tools.
* :doc:`Compare R and Python <compare>` using fixture reports with stated limits.
* Explore :doc:`21 focused tutorial topics <examples/index>`, each with a
  question and a runnable command.

The project follows a practical analysis path: calculate study effects, fit a
model, interpret uncertainty, and inspect study-level results. Its tutorials
use versioned fixtures with recorded provenance. A checked fixture establishes
agreement only for the named data, options, and outputs; it does not establish
general API parity.

The project team intended for this port is Shinichi Nakagawa, Yefeng Yang, and
Wolfgang Viechtbauer. Wolfgang Viechtbauer is also the author of the upstream R
package; that upstream authorship is distinct from this port's intended team.

.. toctree::
   :caption: Start here
   :hidden:
   :maxdepth: 1

   getting-started
   compare
   news
   citation

.. toctree::
   :caption: Reference
   :hidden:
   :maxdepth: 2

   reference/index

.. toctree::
   :caption: Articles
   :hidden:
   :maxdepth: 2

   bcg
   dependent
   examples/index
