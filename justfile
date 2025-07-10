test:
    pytest schedule

type:
    mypy --strict --pretty schedule
    basedpyright schedule

architect:
    tach check

lint:
    ruff format schedule
    ruff check --fix schedule

all: test type lint architect
