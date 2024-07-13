===============
Special Classes
===============

.. _IPC Overview:

``IPC``
*******

The ``IPC`` class has the following methods available for use:

- ``IPC.request(args)`` (see the :doc:`command-sheet` for usage)
- ``IPC.cancel_request(command: str)`` (see the :ref:`Commands Overview` section on the :doc:`variables` page)
- ``IPC.update_file(file: str, current_state: str)`` (current state simply means the current file contents)
- ``IPC.remove_file(file: str)``
- ``IPC.kill_IPC()``

.. _Request Overview:

``Response``
************

The ``Response`` TypedDict classs allows for type checking when handling output from ``Salve``. To access the resulut of the command simply use ``some_response["result"]``.

.. |br| raw:: html

   <br />

|br|

Now that you've finished this section, you can move onwards to the :doc:`variables` page!
