#!/bin/bash

# entrypoint.sh: overwrites the default dbt docker image entrypoint

export EXECUTION_DAY=$(date -I)

dbt run