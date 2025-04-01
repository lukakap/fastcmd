# FastCmd Makefile

.PHONY: tests lint base-build update-requirements-dev update-requirements run

tests:
	docker-compose run --rm pytest

lint:
	docker-compose run --rm lint

base-build:
	docker build -t fastcmd-base -f docker/Dockerfile.dev .

update-requirements-dev:
	docker-compose build update-deps
	docker-compose run --rm update-deps

update-requirements:
	docker-compose build update-main-deps
	docker-compose run --rm update-main-deps

run:
	docker-compose run --rm app
	