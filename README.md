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
If port is occupied, either change the port or kill existing process:
```
kill -9 $(lsof -t -i:8000) 2>/dev/null || true
```

It will be accessible on localhost:8000
