test:
    ruff format schedule
    ruff check --fix schedule
    mypy --strict --pretty schedule
    basedpyright schedule
    pytest schedule
