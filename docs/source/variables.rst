===========================
Special Variables and Types
===========================

.. _Token Overview:

``Token``
*********

The ``Token`` type is, in reality, just a type alias of `tuple[tuple[int, int], int, str]``. Despite simply being a ``tuple``, the ``Token`` is likely the most used data type in ``Salve`` and is the most frequently returned data type to the user. That being said, let me explain what it really is.

The ``Token`` type contains three parts: the start index, its length, and its type. The start index is that ``tuple`` at the beginning of the main ``tuple`` and the first index is the line the ``Token`` takes place on and the second is the column. ``Token``'s start at 1, 0 so you may need to do a -1 or a +1 depending on how you use this data. The second ``int`` is the length of the ``Token`  and the ``str`` is the type. You will use these very often so its never a bad idea to get very familiar with them.

.. _Generic Tokens Overview:

``generic_tokens``
******************

The ``generic_tokens`` ``list`` provides all the generic ``Token`` types you will encounter when using ``Salve``. Simply print this out to get a good idea of what ``Token`` types you will be working with when using ``Salve`` and yoiu will never need to be worried about being surprised by random ``Token`` types.

.. _Commands Overview:

``COMMANDS``
************

``COMMANDS`` is a ``list`` of ``str``'s that allows the user to see all the options available to them when they are offline. If you are online, though, just use the :doc:`command-sheet` page.

.. _Command Overview:

``COMMAND``'s
*************

The ``COMMAND`` variable is a ``str`` type alias used to hopefully prevent spelling mistakes. You see it is not hard to mistype things like ``"autocomplete"`` as `"autocopmlete"` and this can cause issues when working on something like this. Sadly most code editors don't give spelling errors to you but what they do give is autocomplete for variables and errors for misspelled variables. These variables, therefore, can be used to spell check in a way and that is exactly what ``Salve`` uses them for. The full list of them is as follows:

- AUTOCOMPLETE
- REPLACEMENTS
- HIGHLIGHT
- EDITORCONFIG
- DEFINITION

.. _Hidden Chars Overview:

``hidden_chars``
****************

The ``hidden_chars`` variable is a ``dict`` used to cross reference the char that the ``Token`` of type ``"Hidden_Char"`` points to and get the name of the char.

.. |br| raw:: html

   <br />

|br|

Now that you've seen all the variables, lets move on to the functions ``Salve`` provides on the :doc:`functions` page.
