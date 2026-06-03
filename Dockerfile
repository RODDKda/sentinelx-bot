FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY app/test_minimal.py .
ENV PORT=8080
CMD ["python", "test_minimal.py"]
