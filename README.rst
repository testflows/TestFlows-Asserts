TestFlows - Asserts
===================

.. warning::

    This module is still work in progress and is currently under development.
    Please use it only for reference.

No magic, intuitive assertion library, with descriptive error messages
that works with Python's *assert* statement. Inspired by *pytest* 
support for assertions and *grappa-py/grappa* descriptive error messages.

Currenly supports only Python 3.

Installation
************

.. code-block:: bash

    $ ./build; ./install

Usage
*****

.. code-block:: python

    from testflows.asserts import error

    assert 1 == 1, error()

When an assertion fails a descriptive error message is produced.
For example

    .. code-block:: python

       from testflows.asserts import error

       assert 1 == 2, error()

produces the following output

    .. code-block::
    
        Traceback (most recent call last):
          File "t.py", line 3, in <module>
            assert 1 == 2, error()
        AssertionError: Oops! Assertion failed
        
        The following assertion was not satisfied
          assert 1 == 2, error()
        
        Assertion values
          assert 1 == 2, error()
                   ^ is = False
          assert 1 == 2, error()
          ^ is False
        
        Where
          File 't.py', line 3 in '<module>'
        
        0|  1|  from testflows.asserts import error
        2|
        3|> assert 1 == 2, error()
        
