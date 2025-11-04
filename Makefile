install:
	poetry install

project:
	poetry run project

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3.12 -m pip install dist/*.whl

lint:
	poetry run ruff check .

source:
	source /home/evgenii/PycharmProjects/project2_-Pogozhev-_-Evgenii-_-DPO_NOD-/.venv/bin/activate