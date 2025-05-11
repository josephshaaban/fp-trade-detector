# Create a virtual environment
Write-Host "Creating virtual environment..."
py -m venv .venv

# Activate the virtual environment
Write-Host "Activating virtual environment..."
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
. .venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Run the main script
Write-Host "Running the project..."
python main.py