"""
Evaluation test cases for DocuMate RAG system.

Each test case includes:
- question: The query to ask
- expected_evidence: Keywords or phrases that should appear in retrieved chunks
- page_numbers: Expected source pages (if known)
- category: Type of question (factual, summary, reasoning)
"""

TEST_CASES = [
    {
        "question": "When was TechVentures Inc. founded?",
        "expected_evidence": ["2018", "founded"],
        "page_numbers": [0],
        "category": "factual"
    },
    {
        "question": "How many employees does TechVentures have?",
        "expected_evidence": ["250", "employees", "people"],
        "page_numbers": [0],
        "category": "factual"
    },
    {
        "question": "What is TechVentures' annual revenue?",
        "expected_evidence": ["45 million", "revenue", "2023"],
        "page_numbers": [0],
        "category": "factual"
    },
    {
        "question": "What are the three main products offered by TechVentures?",
        "expected_evidence": ["NLP Suite", "VisionAI", "PredictPro"],
        "page_numbers": [1],
        "category": "summary"
    },
    {
        "question": "How much does the VisionAI enterprise plan cost?",
        "expected_evidence": ["2,000", "VisionAI", "enterprise"],
        "page_numbers": [1],
        "category": "factual"
    },
    {
        "question": "Who is the CEO of TechVentures?",
        "expected_evidence": ["Sarah Chen", "CEO"],
        "page_numbers": [2],
        "category": "factual"
    },
    {
        "question": "What is the company's uptime SLA?",
        "expected_evidence": ["99.9%", "uptime", "SLA"],
        "page_numbers": [1],
        "category": "factual"
    },
    {
        "question": "How much funding has TechVentures raised?",
        "expected_evidence": ["30 million", "Series B", "Sequoia"],
        "page_numbers": [2],
        "category": "factual"
    },
    {
        "question": "What is the company's mission?",
        "expected_evidence": ["democratize AI", "accessible", "businesses"],
        "page_numbers": [0],
        "category": "summary"
    },
    {
        "question": "Where are TechVentures' office locations?",
        "expected_evidence": ["San Francisco", "New York", "Austin"],
        "page_numbers": [0],
        "category": "factual"
    }
]
