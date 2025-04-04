test:
    pytest schedule
    basedpyright schedule
    mypy --strict --pretty schedule
    ruff format schedule
    ruff check --fix schedule
