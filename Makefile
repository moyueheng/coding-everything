.PHONY: help install update uninstall status test

help:
	@printf "make install\nmake update\nmake uninstall\nmake status\nmake test\n"

install:
	uv run python scripts/install_skills.py install

update:
	uv run python scripts/install_skills.py update

uninstall:
	uv run python scripts/install_skills.py uninstall

status:
	uv run python scripts/install_skills.py status

test:
	uv run python -m unittest tests.test_install_skills -v
