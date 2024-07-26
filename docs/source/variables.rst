===========================
Special Variables and Types
===========================

.. _Token and GENERIC_TOKENS Overview:

``Token`` and ``GENERIC_TOKENS``
********************************

See `Token Tools Documentation <https://token-tools.readthedocs.io/en/stable/variables/#variables>`_ for details. Note that ``Token`` is a very common return type used by ``Salve``.

.. _Commands Overview:

``COMMANDS``
************

``COMMANDS`` is a ``list`` of ``str``'s that allows the user to see all the options available to them when they are offline. If you are online, though, just use the :doc:`command-sheet` page.

.. _Command Overview:

``COMMAND``'s
*************

The ``COMMAND`` variable is a ``str`` type alias's used to prevent spelling mistakes. It is not hard to mistype things like ``"autocomplete"`` as `"autocopmlete"` and this can cause issues when working on something like this. Sadly most code editors don't give spelling errors to you but what they do give is autocomplete for variables and errors for misspelled variables. These variables, therefore, can be used for spell checking in a way and that is exactly what ``Salve`` uses them for. The full list of them is as follows:

- ``AUTOCOMPLETE``
- ``REPLACEMENTS``
- ``HIGHLIGHT``
- ``EDITORCONFIG``
- ``DEFINITION``

.. _Hidden Chars Overview:

``hidden_chars``
****************

The ``hidden_chars`` variable is a ``dict`` used to cross reference the char that the ``Token`` of type ``"Hidden_Char"`` points to for the name of the char.

.. |br| raw:: html

   <br />

|br|

Now that you've seen all the variables, lets move on to the functions ``Salve`` provides on the :doc:`functions` page.
