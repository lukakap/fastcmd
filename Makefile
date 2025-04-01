# FastCmd Makefile

.PHONY: tests lint base-build update-requirements-dev

tests:
	docker-compose run --rm pytest

lint:
	docker-compose run --rm lint

base-build:
	docker build -t fastcmd-base -f docker/Dockerfile .

update-requirements-dev:
	docker-compose build update-deps
	docker-compose run --rm update-deps