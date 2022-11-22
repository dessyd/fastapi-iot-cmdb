#!/bin/bash
docker compose down -v
docker compose up -d
sleep 2
uvicorn app.main:app --reload
