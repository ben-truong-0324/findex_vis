FROM python:3.13.1

WORKDIR /app

COPY environment.yml .

# Install Miniconda and use Conda to create environment
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    /opt/conda/bin/conda env create -f environment.yml && \
    echo "source /opt/conda/bin/activate myenv" >> ~/.bashrc

COPY . .

SHELL ["/bin/bash", "-c"]

# Activate environment when opening the container
CMD ["/bin/bash"]
