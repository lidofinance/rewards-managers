# LIDO / 1inch co-incentivization integration

## Flow
Deployment, initalization and usage flows are described in separate [FLOW document](./FLOW.md).

## Installation
To use the tools provided by this project, please pull the repository from GitHub and install its dependencies as follows. It is recommended to use a Python virtual environment.
```bash
npm install
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements-dev.txt
```
Compile the smart contracts:
```bash
brownie compile # add `--size` to see contract compiled sizes
```