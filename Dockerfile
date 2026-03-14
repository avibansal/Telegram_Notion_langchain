# Use a Python image with uv pre-installed directly from Astral
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Compile bytecode to improve startup time
ENV UV_COMPILE_BYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Copy dependency files first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies before copying the rest of the application.
# --frozen ensures the lockfile is strictly respected.
# --no-install-project skips installing the project code (since we haven't copied it yet).
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code into the container
COPY . .

# Run a second sync to install the project packages if needed
RUN uv sync --frozen --no-dev

# Run the bot when the container launches.
# If you eventually move all logic to src/main.py, update this CMD!
CMD ["uv", "run", "python", "src/main.py"]
