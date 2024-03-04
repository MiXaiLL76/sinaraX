FORMAT_DIRS = ./sinaraX
LINE_LENGTH = 80

format:
	python3 -m black --line-length $(LINE_LENGTH) $(FORMAT_DIRS)
	python3 -m isort --line-length $(LINE_LENGTH) --profile black $(FORMAT_DIRS)
	$(MAKE) linter

linter:
	python3 -m black --line-length $(LINE_LENGTH) $(FORMAT_DIRS) --check --diff
	python3 -m isort --line-length $(LINE_LENGTH) --profile black $(FORMAT_DIRS) --check --diff
	flake8 --max-line-length $(LINE_LENGTH) $(FORMAT_DIRS)