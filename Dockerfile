FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv pip install .
COPY . .
CMD ["uvicorn", "agentic.main:app", "--host", "0.0.0.0", "--port", "8000"]