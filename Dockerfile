FROM python:3.11-slim

WORKDIR /app

# Copy only the dependency file first to leverage Docker cache
COPY dependencies.txt .

# Install dependencies
RUN pip install --no-cache-dir -r dependencies.txt

# Copy application files
COPY . .

# Create a volume for the database
VOLUME /app/data

# Expose ports for both FastAPI and Streamlit
EXPOSE 8000 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OPENAI_API_KEY=""
ENV STREAMLIT_SERVER_PORT=5000
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Run the application
CMD ["python", "main.py"]