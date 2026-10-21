FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home --uid 10001 app && chown -R app:app /app
USER app
CMD ["uvicorn","app.main:app","--host", "0.0.0.0","--port", "8000"]
