FROM python:3.10-slim

# Install system dependencies: git, ffmpeg, build tools, curl, and rust
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    build-essential \
    curl && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Agree to Coqui license
ENV COQUI_TOS_AGREED=1
ENV COQUI_NON_COMMERCIAL=1

COPY ./models /app/models

# Add Rust to PATH
ENV PATH="/root/.cargo/bin:${PATH}"
ENV PIP_DEFAULT_TIMEOUT=300

# Set workdir and copy files
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port used by FastAPI
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



