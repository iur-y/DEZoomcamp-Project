#!/bin/bash

# init2-apply.sh: does terraform apply interactively

# check if init1-push.sh was executed
if [ ! -e "./init1-done" ]; then
	echo "You must execute init1-push.sh first" 2>&1;
	exit 1
fi

terraform apply
