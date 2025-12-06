# ============================
# Stage 1: Builder
# ============================
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Copy only requirements for dependency install (better caching)
COPY requirements.txt .

# Install dependencies into a separate prefix we can copy later
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt && \
    rm -rf /root/.cache/pip


# ============================
# Stage 2: Runtime
# ============================
FROM python:3.11-slim

# Set timezone to UTC
ENV TZ=UTC

# Set working directory
WORKDIR /app

# Install system dependencies: cron + tzdata
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code and keys into container
COPY app ./app
COPY scripts ./scripts
COPY cron ./cron
COPY student_private.pem student_public.pem instructor_public.pem ./

# Fix Windows CRLF -> Unix LF, then install cron job
RUN sed -i 's/\r$//' cron/2fa-cron && \
    chmod 644 cron/2fa-cron && \
    crontab cron/2fa-cron

# Create volume mount points for persistent data
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Declare volumes (for Docker)
VOLUME ["/data", "/cron"]

# Expose API port
EXPOSE 8080

# Start cron and the FastAPI server when container starts
CMD service cron start && \
    uvicorn app.main:app --host 0.0.0.0 --port 8080
