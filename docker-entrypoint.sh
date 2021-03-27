#!/usr/bin/env bash

export PYTHONPATH=$PWD
cd app/db && alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload