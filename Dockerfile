FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY seed_db.py ./
RUN useradd --system --no-create-home transitops && chown -R transitops /app
USER transitops
WORKDIR /app/backend
EXPOSE 8000
# 1) apply migrations + create roles/admin (idempotent)  2) start the API
CMD ["sh", "-c", "python ../seed_db.py && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
