## Container Testing

The script [test/test.pl](test/test.pl) is used to test the containers. It
is usually invoked as:

```sh
     make test
```

If a test fails, the folowing at the command line might give additional information:

```sh
    cd test && ./test.pl --debug
```

## Adding tests

Tests are just Perl subroutines that return a pair:

```
    (status, description)
```

where:

    1. `status` is  ``1`` if the test was successful and ``0`` otherwise.
    2. ``description`` is a brief description of the test.

Tests should try not to output anything else. However if the global variable ``$debug`` is true,
useful debugging messages should be printed to STDOUT.

The ``test.pl`` script runs in stages. During each stage, it runs the tests in a given list.

Currently, the stages are:

| Stage | List | Description                      |
|-------|:-----------------:|:-----------------------------------------------------|
| 0     | ``@preTests`` |  Tests to run before the server container is started |
| 1     | ``@startTests`` | Tests that test whether the server container was started |
| 2     | ``@postTests``  | Tests to run after the container is started |

Each list contains array references. The first element of each reference is the subroutine to run.
The other elements are passed to that subroutine as arguments.

To add a test, create a new subroutine in test.pl and add it to the appropriate list.
