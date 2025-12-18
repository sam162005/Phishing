FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose Flask port
EXPOSE 5000

# Start app using gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
