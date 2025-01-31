#!/bin/bash

# Absolute file paths
PROJECT_DIR="/Users/xewe/Documents/Programming/Python/PC-Confirmation-Email-Sender"
PYTHON_SCRIPT="$PROJECT_DIR/main.py"
ICS_FILE="$PROJECT_DIR/event.ics"
VENV_DIR="$PROJECT_DIR/.venv"

# Change to the project directory
cd "$PROJECT_DIR" || {
    echo "Error: Failed to change directory to $PROJECT_DIR"
    exit 1
}

# Activate the virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
else
    echo "Error: Virtual environment not found at $VENV_DIR"
    exit 1
fi

# Run the Python script
python "$PYTHON_SCRIPT"

# Check if the event.ics file was created
if [ -f "$ICS_FILE" ]; then
    echo "Opening the calendar event file..."
    open "$ICS_FILE"
else
    echo "Error: The event.ics file was not created."
    exit 1
fi

# Deactivate the virtual environment
deactivate

