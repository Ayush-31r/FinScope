FROM python:3.12-slim

WORKDIR /app

# Install CPU-only torch first before everything else
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install the rest of dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Pull indexes then start server
CMD python hf_index_storage.py pull && python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
