# stock-market

## Initialize Project

To initialize virtual enviroment:
```
uv venv
uv sync
source .venv/bin/activate
```


## Set Up Commit Hooks

To set up commit hooks, run the following command:
```
pre-commit install
```


## Run Locally

To start the server:
```
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

It will be accessible on localhost:8000
