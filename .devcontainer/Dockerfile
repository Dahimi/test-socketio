# Use the official Python image for backend dependencies
FROM mcr.microsoft.com/vscode/devcontainers/python:3.12

# Install Node.js for frontend dependencies
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install global npm packages
RUN npm install -g npm artillery

# Set up backend environment
WORKDIR /workspace/backend
COPY backend/ ./
RUN pip install --no-cache-dir -r requirements.txt

# Set up frontend environment
WORKDIR /workspace/frontend
COPY frontend/ ./
RUN npm install

# Set proper permissions for the non-root user
RUN chown -R vscode:vscode /workspace/
# Switch to the non-root user
USER vscode

# Copy load-test directory
WORKDIR /workspace/load-test
COPY load-test .

# Set the default working directory back to the workspace root
WORKDIR /workspace
