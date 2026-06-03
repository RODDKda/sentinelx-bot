FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data

# Read PORT from Railway environment, default 8000
ENV PORT=8000

CMD python -c "import os; import uvicorn; port=int(os.environ.get('PORT',8000)); uvicorn.run('app.main:app',host='0.0.0.0',port=port)"
