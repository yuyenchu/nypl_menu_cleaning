# Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV PATH="/home/dev/.local/bin:$PATH"

# Install necessary packages
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    openssh-server \
    sudo \
    unzip \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -ms /bin/bash dev && \
    echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set up SSH
RUN mkdir /var/run/sshd

# Add VS Code Server (code-server)
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Set up working directory and permissions
USER dev
WORKDIR /home/dev
RUN mkdir -p ~/.config/code-server

# Configure code-server to not require password and listen on localhost only
RUN echo 'bind-addr: 127.0.0.1:8080\nauth: none\ncert: false' > ~/.config/code-server/config.yaml

# Back to root to copy authorized_keys
USER root

# Copy SSH public key into container (this will be mounted as volume in practice)
RUN mkdir -p /home/dev/.ssh && \
    chown -R dev:dev /home/dev/.ssh && \
    chmod 700 /home/dev/.ssh

    
COPY ./requirements.txt /home/dev/requirements.txt
RUN pip install -r /home/dev/requirements.txt
RUN pip cache purge

EXPOSE 22
RUN echo "HTTP_PROXY=http://squid-proxy:3128" >> /etc/environment && \
    echo "HTTPS_PROXY=http://squid-proxy:3128" >> /etc/environment && \
    echo "NO_PROXY=localhost,127.0.0.1,mysql" >> /etc/environment
CMD /bin/bash -c "/usr/sbin/sshd && sudo -u dev code-server"

