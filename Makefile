PY = python3
NAME = fly_in.py
CFG = config.txt
VENV = .env

VENV_PYTHON = $(VENV)/bin/python

## Install project dependencies
install:
	$(PY) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install -r requirements.txt
	@echo "Virtual enviroment ready."
	@echo "Activate it manually with: source $(VENV)/bin/activate"
	
## Execute the main script of your project
run: install
	$(VENV_PYTHON) $(NAME) $(CFG)
	
## Run the main script in debug mode using Python's built in debugger
debug: install
	$(VENV_PYTHON) -m pdb $(NAME) $(CFG)

## Remove build artifacts and virtual environment
clean:
	@echo "Cleaning caches..."
	@find . -type d \( -name '__pycache__' -o -name '.mypy_cache' -o -name '.pytest_cache' \) -prune -exec rm -rf {} +
	@echo "Removing venv..."
	@rm -rf $(VENV)

## Check code style with flake8 and mypy
lint: install
	@echo "Checking standard coding..."
	@-$(VENV_PYTHON) -m flake8 .
	@echo "\nChecking  static type checking..."
	@-$(VENV_PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

## Check code style with flake8 and mypy --strict
lint-strict: install
	@echo "Checking standard coding..."
	@-$(VENV_PYTHON) -m flake8 .
	@echo "\nChecking  static type checking strictingly..."
	@-$(VENV_PYTHON) -m mypy . --strict

.PHONY: install run debug clean lint lint-strict

