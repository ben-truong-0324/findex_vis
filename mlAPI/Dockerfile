# Use an official slim Python image
FROM python:3.9-slim

# Build argument to decide if CUDA packages should be installed.
# Default is 'no' (i.e. don't install CUDA) which is suitable for Mac dev.
ARG INSTALL_CUDA=yes

# Set the working directory in the container.
WORKDIR /app

# ENV PYTHONPATH="${PYTHONPATH}:/app"


COPY requirements/base.txt requirements/base.txt
COPY requirements/dev.txt requirements/dev.txt



# Install system dependencies and Python + pip3
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    python3-pip \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip3 and install PyTorch based on CUDA flag
RUN pip3 install --upgrade pip && \
    if [ "$INSTALL_CUDA" = "yes" ]; then \
        pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 ; \
    else \
        pip3 install torch torchvision torchaudio ; \
    fi && \
    pip3 install -r requirements/base.txt && \
    pip3 install -r requirements/dev.txt

# Copy the rest of your application code.
COPY . .

# Expose the port where your FastAPI app is running.
EXPOSE 8000

# Set the command to launch the app with Uvicorn.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
