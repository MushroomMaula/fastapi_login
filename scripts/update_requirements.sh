#!/usr/bin/env bash

poetry export -o requirements.txt --without-hashes --with dev -E asymmetric
poetry export -o requirements-example.txt --without-hashes --with example
cp requirements-example.txt examples/full-example/requirements.txt
cp requirements-example.txt examples/simple/requirements.txt
cp requirements-example.txt examples/sqlalchemy/requirements.txt
rm requirements-example.txt
