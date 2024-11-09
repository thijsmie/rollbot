all: lint format test

lint:
	poetry run ruff check --fix src tests

format:
	poetry run ruff format src tests

test:
	poetry run pytest

.PHONY: lint format test
