# Contributing to KubeHeal AI

## Development Setup
```bash
git clone https://github.com/harshdwivediiiii/Kubeheal-Ai.git
cd Kubeheal-Ai
python3 -m venv .venv
source .venv/bin/activate
make install
pre-commit install
```

## Code Style
- Python: Black + Ruff
- Type hints required for all functions
- Docstrings for public APIs

## Pull Request Process
1. Create a feature branch
2. Write tests for new features
3. Run `make lint` and `make test`
4. Update documentation
5. Submit PR with clear description

## Commit Messages
```
feat: add new feature
fix: fix bug description
docs: update documentation
refactor: improve code structure
test: add tests
chore: maintenance tasks
```
