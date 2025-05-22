# Use an official Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /api

# Copy project files into the container
COPY . /api

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]