test:
    pytest schedule
    mypy --strict --pretty schedule
    basedpyright schedule
    tach check
    ruff format schedule
    ruff check --fix schedule
