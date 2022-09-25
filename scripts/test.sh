#! /usr/bin/env bash

set -e
set -x

# pytest --doctest-modules src  # Uncomment when to run doctests
pytest --cov-report=term-missing:skip-covered ${@}
