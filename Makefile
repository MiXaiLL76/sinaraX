wheel:
	pipx run build --wheel .

sdist:
	pipx run build --sdist .

FORMAT_DIRS = ./sinaraX ./tests
LINE_LENGTH = 80
BLACK_CONFIG = --preview --enable-unstable-feature string_processing

format:
	pre-commit run --all-files

clean:
	rm -rf build dist *.egg-info sinaraX/*.egg-info
	pip3 uninstall sinaraX -y

test:
	pip3 install -e .
	python3 tests/test_server.py
	pip3 uninstall sinaraX -y

install: sdist
	pip3 install dist/*
