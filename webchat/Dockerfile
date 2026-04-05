FROM python:3.14-slim-bookworm
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn httpx
COPY webchat/app.py /app/app.py
RUN mkdir -p /app/data
EXPOSE 8083
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8083"]
