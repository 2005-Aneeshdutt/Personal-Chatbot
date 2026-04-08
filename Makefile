# Optional: make install && make prepare && make train && make eval
.PHONY: install prepare train eval eval-real run test

install:
	python -m pip install -r requirements.txt

prepare:
	python prepare_datasets.py

train:
	python train_intent_model.py

eval:
	python evaluate_chatbot.py

eval-real:
	python prepare_real_intent_splits.py
	python evaluate_real_intent_benchmark.py

all: install prepare train

test:
	pytest tests/test_smoke.py -q

run:
	streamlit run app.py
