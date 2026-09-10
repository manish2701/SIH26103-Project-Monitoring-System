FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend
COPY ml ./ml
COPY data ./data
COPY sih26103.db ./data/sih26103.db
COPY start.sh .

RUN chmod +x start.sh

EXPOSE 8501

CMD ["./start.sh"]
