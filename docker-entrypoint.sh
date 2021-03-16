#!/usr/bin/env bash

python -m app.main
cd app/db && alembic upgrade head