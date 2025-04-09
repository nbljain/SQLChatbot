FROM python:3.11-slim

WORKDIR /app

# Copy the entire project directory
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r docker-requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=5000
ENV HOST=0.0.0.0

# Expose ports for FastAPI backend and Streamlit frontend
EXPOSE 8000
EXPOSE 5000

# Create a data directory for the database
RUN mkdir -p /app/data/csv

# Create entrypoint script
RUN echo '#!/bin/bash\n\
python -m src.api.fastapi_backend & \
sleep 3 && \
streamlit run src/frontend/app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]