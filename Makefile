# FastCmd Makefile

.PHONY: tests lint base-build

tests:
	docker-compose run --rm pytest

lint:
	docker-compose run --rm lint

base-build:
	docker build -t fastcmd-base -f docker/Dockerfile .