#!/bin/bash

echo "Starting Legal Vacancy Tracker..."

if [ ! -d "venv" ]; then
    echo "Virtual environment not found! Please create it using: python -m venv venv"
    exit 1
fi

source venv/bin/activate
python main.py "$@"
