#!/usr/bin/env bash

poetry export -o requirements.txt --without-hashes --with dev -E asymmetric
