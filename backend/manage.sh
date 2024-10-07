#!/usr/bin/env bash
docker compose run -w /usr/src/app/ --rm web python manage.py "$@"
