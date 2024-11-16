# Python-utilities

Some utilities in Python - copy&amp;paste source when needed

# Prerequisites

```bash
pip install colorama
pip install psutil
pip install confluent-kafka
pip install networkx
pip install fastavro
pip install pygccxml
```

# Installation

```bash
# might need to install poetry first (here for debian)!
 sudo apt install python3-poetry
```
```bash
# build the wheel
poetry build

# install the wheel
pip install dist/tools-0.1.0-py3-none-any.whl
```