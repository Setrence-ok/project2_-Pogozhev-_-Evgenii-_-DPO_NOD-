install:
	poetry install

project:
	poetry run database

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3.12 -m pip install dist/*.whl

lint:
	poetry run ruff check .

env:
	poetry env activate