FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data

# Railway injects PORT; use it directly via Python
CMD ["python", "-c", "import os,uvicorn; p=int(os.environ.get('PORT','8000')); print(f'Binding to 0.0.0.0:{p}'); uvicorn.run('app.main:app',host='0.0.0.0',port=p)"]
