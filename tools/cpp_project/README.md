# Build container
```bash
docker compose build
```

# Run
```bash
docker run  -it -v $(realpath ../..):$(realpath ../..) python_runner:0.0.1
```
