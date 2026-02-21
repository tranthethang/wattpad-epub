# Stage 1: Build dependencies
FROM python:3.10-slim as builder

WORKDIR /app
COPY requirements.txt .

# Install dependencies to a temporary path
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final Runtime
FROM python:3.10-slim

ARG WWWUSER
ARG WWWGROUP

WORKDIR /app

# Create 'agent' user and group, handling cases where GID/UID might already exist
RUN if ! grep -q ":${WWWGROUP}:" /etc/group; then \
        groupadd -g ${WWWGROUP} agent; \
    fi && \
    if ! grep -q ":${WWWUSER}:" /etc/passwd; then \
        useradd -m -u ${WWWUSER} -g ${WWWGROUP} agent; \
    fi

# Install Playwright system dependencies for chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrender1 \
    libxrandr2 \
    libgbm1 \
    libdrm2 \
    libxkbcommon0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed libraries from builder stage
COPY --from=builder /install /usr/local

# Install Playwright chromium
RUN python -m playwright install chromium

# Switch to non-root user
USER agent

# Default command for development (Port 80)
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
