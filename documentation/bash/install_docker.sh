#!/bin/bash

if ! command -v docker &> /dev/null
then
    echo "Docker could not be found. Installing Docker..."
    # Update the package database
    sudo apt-get update

    # Install packages to allow apt to use a repository over HTTPS
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

    # Add Docker’s official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Add the Docker repository to APT sources
    echo \
      "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Update the package database (again) with the Docker packages
    sudo apt-get update

    # Install Docker
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io

    # Add the current user to the docker group so that you don't have to use sudo for docker commands
    sudo usermod -aG docker $USER

    echo "Docker has been installed."
  else
    echo "Docker is already installed. Skipping installation."
fi

if ! command -v docker-compose &> /dev/null
then
    echo "Docker Compose could not be found. Installing Docker Compose..."
    sudo apt-get install docker-compose -y
    echo "Docker Compose has been installed."
else
    echo "Docker Compose is already installed. Skipping installation."
fi

# Install Docker Compose
