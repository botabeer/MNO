FROM python:3.11-slim

WORKDIR /app

# نسخ الملفات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# إنشاء المجلدات
RUN mkdir -p games

# المنفذ
EXPOSE 5000

# تشغيل التطبيق
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120"]
