# Use an official slim Python image
FROM python:3.9-slim

# Build argument to decide if CUDA packages should be installed.
# Default is 'no' (i.e. don't install CUDA) which is suitable for Mac dev.
ARG INSTALL_CUDA=no

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements files first to leverage Docker layer caching.
COPY requirements/base.txt requirements/base.txt
COPY requirements/dev.txt requirements/dev.txt

# Conditionally remove the CUDA-specific package from base.txt if CUDA is not needed.
RUN if [ "$INSTALL_CUDA" = "no" ]; then \
      sed -i '/[pP]ytorch-cuda/d' requirements/base.txt; \
    fi && \
    # Upgrade pip and install requirements from both files
    pip install --upgrade pip && \
    pip install -r requirements/base.txt && \
    pip install -r requirements/dev.txt

# Copy the rest of your application code.
COPY . .

# Expose the port where your FastAPI app is running.
EXPOSE 8000

# Set the command to launch the app with Uvicorn.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
