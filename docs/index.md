# embedded-lab

Low‑level driver development for Raspberry Pi and other embedded Linux platforms. Includes kernel modules, I²C devices, and hardware experimentation.

## Requirements

1. Update the system
    ```bash
    sudo apt update
    sudo apt full-upgrade -y
    sudo apt autoremove -y
    ```

2. Essential packages:
    ```bash
    sudo apt install -y \
        git \
        curl \
        wget \
        vim \
        nano \
        htop \
        tree \
        unzip \
        zip \
        jq \
        ca-certificates \
        gnupg \
        build-essential \
        pkg-config \
        cmake \
        gdb \
        openssh-client \
        openssh-server \
        rsync \
        lsof \
        net-tools \
        dnsutils \
        iputils-ping
    ```

3. Python:
    ```bash
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv

    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

4. Raspberry Pi hardware and GPIO

    ```bash
    sudo apt install -y i2c-tools
    ```
