# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies:
# - apt-get update: Updates the list of available packages
# - unixodbc: The Unix ODBC driver manager
# - unixodbc-dev: Development headers for building ODBC-related Python packages (e.g., pyodbc)
# - --no-install-recommends: Avoids installing recommended but not strictly necessary packages
# - rm -rf /var/lib/apt/lists/*: Cleans up apt cache to keep the image size small
RUN apt-get update && \
    apt-get install -y --no-install-recommends unixodbc unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

# Install uv:
# uv is a fast Python package installer and resolver, designed as a drop-in replacement for pip.
RUN pip install uv

# (Optional) If your map_server.py has Python dependencies, list them in a requirements.txt
# and install them using uv. Uncomment the following lines if needed:
# COPY requirements.txt .
# RUN uv pip install -r requirements.txt

# Create a placeholder map_server.py file.
# In a real application, you would replace this with:
# COPY map_server.py .
RUN echo "import os\n" \
     "import sys\n" \
     "import time\n" \
     "print(f\"Map server started using uv and Python {sys.version.split(' ')[0]}!\")\n" \
     "print(f\"Environment variable EXAMPLE_VAR: {os.getenv('EXAMPLE_VAR', 'Not Set')}\")\n" \
     "print(\"Server running... Press Ctrl+C to exit.\")\n" \
     "try:\n" \
     "    while True:\n" \
     "        time.sleep(1)\n" \
     "except KeyboardInterrupt:\n" \
     "    print(\"Map server stopped.\")" > map_server.py

# Expose the port your map server might listen on (e.g., 8000 for a web server)
# This is illustrative; adjust if your map server uses a different port or none.
EXPOSE 8000

# Set the entrypoint for the container.
# This command will be executed when the container starts.
# We use 'uv run python' to execute the Python script.
# The 'uv run' command ensures that the script runs within a uv-managed environment.
ENTRYPOINT ["uv", "run", "python", "map_server.py"]

# You can also define a default command that can be overridden at runtime.
# For example, to pass an argument:
# CMD ["--some-arg", "value"]
# If you run `docker run my-image`, it will execute `uv run python map_server.py --some-arg value`
# If you run `docker run my-image /bin/bash`, it will override the CMD and run bash.
