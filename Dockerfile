# Use official Playwright Python image with all dependencies pre-installed
FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

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

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Use default Playwright browsers location from base image
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Ensure all app files are owned by agent user
RUN chown -R ${WWWUSER}:${WWWGROUP} /app

# Switch to non-root user
USER agent

# Default command for development (Port 80)
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
