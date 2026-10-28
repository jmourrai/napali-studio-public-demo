FROM python:3.12-slim
WORKDIR /demo
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DEMO_DB_PATH=/demo/.data/workflows.sqlite
COPY pyproject.toml ./
COPY app ./app
COPY web ./web
RUN pip install --no-cache-dir . && mkdir -p /demo/.data && useradd -u 10001 -m demo && chown -R demo:demo /demo/.data
USER demo
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
