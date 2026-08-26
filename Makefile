.PHONY: help setup eval clean test

help:
	@echo "DocuMate - RAG Document Q&A System"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup       - Install dependencies and set up environment"
	@echo "  make eval        - Run evaluation harness"
	@echo "  make fixture     - Generate test fixture PDF"
	@echo "  make clean       - Clean generated files"
	@echo "  make test        - Run basic smoke tests"
	@echo ""

setup:
	@echo "Setting up backend..."
	cd backend && pip install -r requirements.txt
	@echo ""
	@echo "Setting up frontend..."
	cd frontend && npm install
	@echo ""
	@echo "Setup complete! Create a .flaskenv file with your configuration."
	@echo "See README.md for details."

fixture:
	@echo "Generating test fixture PDF..."
	cd evals && python3 create_fixture_pdf.py

eval: fixture
	@echo "Running evaluation harness..."
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "ERROR: OPENAI_API_KEY not set"; \
		echo "Run: export OPENAI_API_KEY='your-key-here'"; \
		exit 1; \
	fi
	cd evals && python3 run_evals.py

clean:
	@echo "Cleaning generated files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -f evals/eval_results.json
	rm -f evals/fixtures/*.pdf
	@echo "Clean complete"

test:
	@echo "Running smoke tests..."
	cd backend && python3 -c "import app; print('✓ Backend imports OK')"
	cd frontend && npm run build --if-present
	@echo "✓ Tests passed"
