# Full setup: deps -> splits -> train -> evaluate (Windows PowerShell)
# Run from project root: .\scripts\run_all.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "Installing dependencies..."
python -m pip install -r requirements.txt

Write-Host "Preparing dataset splits..."
python prepare_datasets.py

Write-Host "Training intent model..."
python train_intent_model.py

Write-Host "Evaluating domain test sets..."
python evaluate_chatbot.py

Write-Host "Done. Start UI with: streamlit run app.py"
