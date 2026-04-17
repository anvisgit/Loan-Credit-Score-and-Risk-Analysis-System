#!/bin/bash

# LoanIQ Project Runner
# This script starts PostgreSQL in Docker, installs dependencies, sets up the database, and runs the Streamlit app.

echo "LoanIQ — One-Command Project Runner"
echo "===================================="

# Step 0: Start PostgreSQL in Docker
echo "0. Starting PostgreSQL in Docker..."
docker run -d --name postgres-loan -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=loandb -p 5432:5432 postgres:13
sleep 5  # Wait for DB to start

# Step 1: Install dependencies
echo "1. Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies. Check Python/pip setup."
    exit 1
fi

# Step 2: Set up database
echo "2. Setting up database..."
python setup_db.py
if [ $? -ne 0 ]; then
    echo "Error: Database setup failed. Ensure PostgreSQL is running and 'loandb' database exists."
    echo "Run: CREATE DATABASE loandb; in psql if needed."
    exit 1
fi

# Step 3: Run the app
echo "3. Launching Streamlit app..."
streamlit run app/main.py