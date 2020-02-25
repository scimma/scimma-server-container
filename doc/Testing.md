## Container Testing

Testing is implemented using [pytest](https://docs.pytest.org/). The test can be run using:

```sh
     make test
```

The tests can be run manually like so:

```sh
    cd test && pytest -v
```

To see the output of tests, pytest can be run with the ``-s`` option:

```sh
    cd test && pytest -s
```

The tests run against a specific tag specified by the environment variable ``SCIMMA_TEST_TAG``. If that 
variable is not specified then the tests run against the tag ``latest``.
