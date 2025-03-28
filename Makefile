# FastCmd Makefile

.PHONY: test docker-test install run clean

# Run tests locally
test:
	python3 -m pytest

# Run tests in Docker
docker-test:
	docker-compose run --rm pytest

# Install development dependencies
install:
	pip install -e .
	# Install dev dependencies if requirements-dev.txt exists
	if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# Run the application
run:
	python3 src/fastcmd.py

# Clean up generated files
clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf build/
	rm -rf dist/

.PHONY: lint

lint:
	@echo "🔧 Running black..."
	black src tests

	@echo "🔧 Running isort..."
	isort src tests

	@echo "🔍 Running flake8..."
	flake8 src tests

	@echo "🧠 Running mypy..."
	mypy src tests