#!/usr/bin/env bash
# Full setup from repo root: bash scripts/run_all.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Installing dependencies..."
python -m pip install -r requirements.txt

echo "Preparing dataset splits..."
python prepare_datasets.py

echo "Training intent model..."
python train_intent_model.py

echo "Evaluating domain test sets..."
python evaluate_chatbot.py

echo "Done. Start UI with: streamlit run app.py"
