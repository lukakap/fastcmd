# FastCmd Makefile

.PHONY: tests lint base-build update-requirements-dev update-requirements run clean-config publish

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

# Run using docker-compose (recommended for development)
run:
	@mkdir -p ${HOME}/.fastcmd/db
	@chmod 700 ${HOME}/.fastcmd
	@chmod 700 ${HOME}/.fastcmd/db
	docker-compose run --rm app

# Clean configuration and database
clean-config:
	@echo "Cleaning configuration and database..."
	@rm -rf ${HOME}/.fastcmd
	@echo "Configuration and database cleaned."

publish:
	@echo "Building FastCmd Docker image..."
	docker build -t lukakap/fastcmd:latest -f docker/Dockerfile.app .
	@echo "Pushing FastCmd Docker image to Docker Hub..."
	docker push lukakap/fastcmd:latest
	@echo "Successfully published FastCmd Docker image!"
	