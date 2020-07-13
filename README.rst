`TestFlows.com Open-Source Software Testing Framework`_ Asserts
=================================================================

.. image:: https://raw.githubusercontent.com/testflows/TestFlows-ArtWork/master/images/testbug-laptop-testflows.png
   :width: 100%
   :alt: test bug
   :align: center

**The asserts module is still work in progress and is currently under development.
Please use it only for reference.**

No magic, intuitive assertion library with descriptive error messages.
Works with Python's `assert statement`_ and is inspired by pytest_
support for assertions and `grappa-py/grappa`_ descriptive error messages.

Currently supports only Python 3.6 or above.

Why
***

* No special assertion methods.
  Uses the default `assert statement`_.
* No magic.
  Assertion statements are not modified and the default AssertionError_
  class is not overridden.
* High performance.
  No extra code is executed if the assertion does not fail unless the assertion has side effects.
* No external dependencies.
* Simple and clean API.
* Compatible with most Python test frameworks.

Usage
*****

Use **error** for a single assert statement

.. code-block:: python

    from testflows.asserts import error

    assert 1 == 1, error()

or use **errors** context manager to wrap multiple assert statements

.. code-block:: python

    from testflows.asserts import errors

    with errors():
        assert 1 == 1
        assert 2 == 2

and if you don't want to abort when an assertion fails and would like to
keep going then the **errors** context manager supports soft assertions through it's
**error** method.

.. code-block:: python

    from testflows.asserts import errors

    with errors() as soft:
        with soft.error():
            assert 1 == 2
        assert 2 == 2

When an assertion fails a descriptive error message is produced.
For example

    .. code-block:: python

       from testflows.asserts import error

       assert 1 == 2, error()

produces the following output

    .. code-block:: bash

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

        0|
        1|  from testflows.asserts import error
        2|
        3|> assert 1 == 2, error()

How
***

The **asserts** module works similarly to the old implementation of
pytest_ assertions. If the assertion fails, the `assert statement`_ is reinterpreted
to produce a detailed error message.

  Therefore, if the assertion statement has a side effect it might not
  work as expected when an assertion fails.

In the pytest_ framework, this problem_ is solved
by rewriting the original assertion.
The **asserts** module solves this problem_ by explicitly using **values** context manager
to store the values of the expression that has a side effect.

Installation
************

.. code-block:: bash

    $ ./build; ./install


where

.. code-block:: bash

    $ ./build

creates a pip installable package in *./dist*, for example

.. code-block:: bash

    $ ls dist/
    testflows.asserts-4.1.190811.155018.tar.gz

and

.. code-block:: bash

    $ ./install

uses *sudo pip install* command to perform the system-wide installation.

Assertions with side-effects
****************************

If assertion has side effects then **values** context manager can be used to
address this problem_.

The example below demonstrates the problem_.

.. code-block:: python

    from testflows.asserts import error

    buf = [1]
    assert buf.append(2) and buf, error()


In the code above, the assertion fails and the **buf** list is modified twice. Once
when the assertion fails and once when the assertion is reinterpreted when
**error()** method is evaluated.

The error message that is produced shows the problem_

.. code-block:: bash

    The following assertion was not satisfied
      assert buf.append(2) and buf, error()

    Assertion values
      assert buf.append(2) and buf, error()
             ^ is [1, 2, 2]
      assert buf.append(2) and buf, error()
             ^ is = <built-in method append of list object at 0x7f13d1c41248>
      assert buf.append(2) and buf, error()
             ^ is = None
      assert buf.append(2) and buf, error()
                               ^ is [1, 2, 2]
      assert buf.append(2) and buf, error()
                           ^ is = None
      assert buf.append(2) and buf, error()
      ^ is False

    Where
      File 't.py', line 4 in '<module>'

    1|  from testflows.asserts import error
    2|
    3|  buf = [1]
    4|> assert buf.append(2) and buf, error()

specifically, the lines below show that value of **buf** is [1,2,2] instead
of the desired value of [1,2]

.. code-block:: bash

    Assertion values
      assert buf.append(2) and buf, error()
             ^ is [1, 2, 2]

In order to work around this problem_, **values** context manager can be used
as follows

.. code-block:: python

    from testflows.asserts import values, error

    buf = [1]
    with values() as that:
        assert that(buf.append(2)) and buf, error()



and it will produce the error message

.. code-block:: bash

    The following assertion was not satisfied
      assert that(buf.append(2)) and buf, error()

    Assertion values
      assert that(buf.append(2)) and buf, error()
             ^ is = None
      assert that(buf.append(2)) and buf, error()
                                     ^ is [1, 2]
      assert that(buf.append(2)) and buf, error()
                                 ^ is = None
      assert that(buf.append(2)) and buf, error()
      ^ is False

    Where
      File 't.py', line 5 in '<module>'

    1|  from testflows.asserts import values, error
    2|
    3|  buf = [1]
    4|  with values() as that:
    5|>     assert that(buf.append(2)) and buf, error()

the lines below show that the **buf** list has the expected value of [1,2]

.. code-block:: bash

      assert that(buf.append(2)) and buf, error()
                                     ^ is [1, 2]

this is because the expression passed to **that** is not reinterpreted and only the
result of the expression is stored and used during the generation of the error message.

  The explicit use of **values** context manager provides a simple solution without
  any need to rewrite the original assertion statement.

.. _problem: http://pybites.blogspot.com/2011/07/behind-scenes-of-pytests-new-assertion.html
.. _AssertionError: https://docs.python.org/3/library/exceptions.html#AssertionError
.. _`assert statement`: https://docs.python.org/3/reference/simple_stmts.html#assert
.. _`grappa-py/grappa`: https://github.com/grappa-py/grappa
.. _pytest: https://docs.pytest.org/en/latest/assert.html
.. _`TestFlows.com Open-Source Software Testing Framework`: https://testflows.com
