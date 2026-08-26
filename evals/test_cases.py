"""
Evaluation test cases for DocuMate RAG system.

Each test case includes:
- question: The query to ask
- expected_evidence: Keywords or phrases that should appear in retrieved chunks
- page_numbers: Expected source pages (if known) - None for URLs
- category: Type of question (factual, summary, reasoning)
- source_type: 'pdf' or 'url' - which fixture to test against
"""

# PDF test cases (TechVentures fixture)
PDF_TEST_CASES = [
    {
        "question": "When was TechVentures Inc. founded?",
        "expected_evidence": ["2018", "founded"],
        "page_numbers": [0],
        "category": "factual",
        "source_type": "pdf"
    },
    {
        "question": "How many employees does TechVentures have?",
        "expected_evidence": ["250", "employees", "people"],
        "page_numbers": [0],
        "category": "factual",
        "source_type": "pdf"
    },
    {
        "question": "What is TechVentures' annual revenue?",
        "expected_evidence": ["45 million", "revenue", "2023"],
        "page_numbers": [0],
        "category": "factual",
        "source_type": "pdf"
    },
    {
        "question": "What are the three main products offered by TechVentures?",
        "expected_evidence": ["NLP Suite", "VisionAI", "PredictPro"],
        "page_numbers": [1],
        "category": "summary",
        "source_type": "pdf"
    },
    {
        "question": "How much does the VisionAI enterprise plan cost?",
        "expected_evidence": ["2,000", "VisionAI", "enterprise"],
        "page_numbers": [1],
        "category": "factual",
        "source_type": "pdf"
    },
    {
        "question": "Who is the CEO of TechVentures?",
        "expected_evidence": ["Sarah Chen", "CEO"],
        "page_numbers": [2],
        "category": "factual",
        "source_type": "pdf"
    },
    {
        "question": "What is the company's uptime SLA?",
        "expected_evidence": ["99.9%", "uptime", "SLA"],
        "page_numbers": [1],
        "category": "factual",
        "source_type": "pdf"
    },
    {
        "question": "How much funding has TechVentures raised?",
        "expected_evidence": ["30 million", "Series B", "Sequoia"],
        "page_numbers": [2],
        "category": "factual",
        "source_type": "pdf"
    },
]

# URL/HTML test cases (CloudTech fixture)
URL_TEST_CASES = [
    {
        "question": "When was CloudTech Solutions founded?",
        "expected_evidence": ["2020", "founded"],
        "page_numbers": None,
        "category": "factual",
        "source_type": "url"
    },
    {
        "question": "How many employees does CloudTech Solutions have?",
        "expected_evidence": ["85", "cloud engineers", "staff"],
        "page_numbers": None,
        "category": "factual",
        "source_type": "url"
    },
    {
        "question": "What is CloudTech's annual recurring revenue?",
        "expected_evidence": ["12 million", "revenue", "2025"],
        "page_numbers": None,
        "category": "factual",
        "source_type": "url"
    },
    {
        "question": "What are the three main service packages offered?",
        "expected_evidence": ["Migration", "Managed Cloud Operations", "Cost Optimization"],
        "page_numbers": None,
        "category": "summary",
        "source_type": "url"
    },
    {
        "question": "What is the uptime SLA for managed cloud operations?",
        "expected_evidence": ["99.95%", "uptime", "SLA"],
        "page_numbers": None,
        "category": "factual",
        "source_type": "url"
    },
    {
        "question": "Who is the CEO of CloudTech Solutions?",
        "expected_evidence": ["Robert Martinez", "CEO"],
        "page_numbers": None,
        "category": "factual",
        "source_type": "url"
    },
    {
        "question": "How much funding has CloudTech raised?",
        "expected_evidence": ["8 million", "Series A", "Benchmark"],
        "page_numbers": None,
        "category": "factual",
        "source_type": "url"
    },
]

# Combined test suite
TEST_CASES = PDF_TEST_CASES + URL_TEST_CASES
