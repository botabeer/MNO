# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Ensure games directory exists
RUN mkdir -p games

# Expose port
EXPOSE 5000

# Set default environment
ENV ENV_MODE=prod
ENV PORT=5000

# Entrypoint script to choose Dev/Prod mode
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
