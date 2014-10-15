#!/bin/bash
celery worker -A vuaro_test_muzeevas -c 2 -E -l INFO -n default -Q default,picture,email