test:
    pytest schedule
    basedpyright schedule
    mypy --strict --pretty schedule
    tach check
    ruff format schedule
    ruff check --fix schedule
