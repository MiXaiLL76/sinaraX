wheel:
	pipx run build --wheel .

sdist:
	pipx run build --sdist .

FORMAT_DIRS = ./sinaraX
LINE_LENGTH = 80
BLACK_CONFIG = --preview --enable-unstable-feature string_processing

format:
	python3 -m black $(BLACK_CONFIG) --line-length $(LINE_LENGTH) $(FORMAT_DIRS)
	python3 -m isort --line-length $(LINE_LENGTH) --profile black $(FORMAT_DIRS)
	$(MAKE) linter

linter:
	python3 -m black $(BLACK_CONFIG) --line-length $(LINE_LENGTH) $(FORMAT_DIRS) --check --diff
	python3 -m isort --line-length $(LINE_LENGTH) --profile black $(FORMAT_DIRS) --check --diff
	flake8 --max-line-length $(LINE_LENGTH) $(FORMAT_DIRS)

clean:
	rm -rf build dist *.egg-info sinaraX/*.egg-info
	pip3 uninstall sinaraX -y

install: sdist
	pip3 install dist/*