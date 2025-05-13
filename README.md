# DowData API

Projeto em FastAPI para obter retornos diários dos componentes do Dow Jones Industrial Average.

## Pré-requisitos
- Python 3.13 ou superior
- UV (Python package manager)
  ```bash
  pip install uv
  ```

## Instalação e execução
1. Na raiz do projeto, instale as dependências definidas em `pyproject.toml`:
   ```bash
   uv sync
   ```
2. Inicie o servidor FastAPI:
   ```bash
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   Alternativamente, use o ponto de entrada do script:
   ```bash
   uv run python main.py
   ```
3. Acesse a API em:
   - http://localhost:8000
   - Documentação interativa: http://localhost:8000/docs
