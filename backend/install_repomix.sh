#!/bin/bash

# Check if Repomix is installed
if ! command -v repomix &> /dev/null; then
    echo "Repomix is not installed. Installing via npm..."

    # Install Node.js (if not already available)
    apt-get update && apt-get install -y nodejs npm

    # Install Repomix globally
    npm install -g repomix || {
        echo "Error installing Repomix via npm"
        exit 1
    }

    echo "Repomix has been installed successfully via npm."
else
    echo "Repomix is already installed."
fi
