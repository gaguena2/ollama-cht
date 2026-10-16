FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ollama_cht ./ollama_cht

EXPOSE 8000

CMD ["uvicorn", "ollama_cht.main:app", "--host", "0.0.0.0", "--port", "8000"]
