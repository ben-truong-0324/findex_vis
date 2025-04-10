# Use official Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose internal container port 5000
EXPOSE 5000

# Run Flask server
CMD ["python", "app.py"]
