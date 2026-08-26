#!/usr/bin/env python3
"""
Evaluation harness for DocuMate RAG system.

Runs test questions against the RAG system and calculates:
- Retrieval hit rate: % of queries where expected evidence is in retrieved chunks
- Groundedness: Basic check that answer contains content from retrieved chunks
- Latency: Average response time
- Token usage: Total tokens consumed

Usage:
    python run_evals.py [--fixture fixtures/test_document.pdf]
"""

import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main.llm.document_rag import (
    extract_lcdocs_from_file, 
    initialize_qa_rag_chain, 
    get_answer_from_rag,
    RETRIEVER
)
from test_cases import TEST_CASES


class EvalMetrics:
    def __init__(self):
        self.total_queries = 0
        self.retrieval_hits = 0
        self.grounded_answers = 0
        self.total_latency_ms = 0
        self.total_tokens = 0
        self.results = []
    
    def add_result(self, test_case, result, retrieved_docs):
        """Record result of a single eval"""
        self.total_queries += 1
        
        # Check retrieval hit rate
        retrieved_text = " ".join([doc.page_content.lower() for doc in retrieved_docs])
        expected_evidence = test_case['expected_evidence']
        evidence_found = sum(1 for evidence in expected_evidence 
                           if any(e.lower() in retrieved_text for e in evidence.split()))
        
        retrieval_hit = evidence_found >= len(expected_evidence) * 0.5
        if retrieval_hit:
            self.retrieval_hits += 1
        
        # Check groundedness (answer contains content from retrieved chunks)
        answer_lower = result['answer'].lower()
        grounded = any(chunk[:50].lower() in answer_lower or 
                      answer_lower[:50] in chunk.lower() 
                      for chunk in retrieved_text.split('\n\n'))
        if grounded:
            self.grounded_answers += 1
        
        # Accumulate metrics
        self.total_latency_ms += result.get('latency_ms', 0)
        self.total_tokens += result.get('token_usage', {}).get('total_tokens', 0)
        
        self.results.append({
            'question': test_case['question'],
            'category': test_case['category'],
            'retrieval_hit': retrieval_hit,
            'grounded': grounded,
            'evidence_found': f"{evidence_found}/{len(expected_evidence)}",
            'latency_ms': result.get('latency_ms', 0),
            'tokens': result.get('token_usage', {}).get('total_tokens', 0),
            'citations': result.get('citations', [])
        })
    
    def print_summary(self):
        """Print evaluation summary"""
        print("\n" + "="*80)
        print("EVALUATION SUMMARY")
        print("="*80)
        print(f"Total queries: {self.total_queries}")
        print(f"Retrieval hit rate: {self.retrieval_hits}/{self.total_queries} "
              f"({100*self.retrieval_hits/self.total_queries:.1f}%)")
        print(f"Grounded answers: {self.grounded_answers}/{self.total_queries} "
              f"({100*self.grounded_answers/self.total_queries:.1f}%)")
        print(f"Average latency: {self.total_latency_ms/self.total_queries:.0f}ms")
        print(f"Total tokens used: {int(self.total_tokens)}")
        print(f"Avg tokens per query: {int(self.total_tokens/self.total_queries)}")
        print("="*80)
        
        # Print detailed results
        print("\nDETAILED RESULTS:")
        print("-"*80)
        for i, result in enumerate(self.results, 1):
            print(f"\n{i}. {result['question']}")
            print(f"   Category: {result['category']}")
            print(f"   Retrieval hit: {'✓' if result['retrieval_hit'] else '✗'} "
                  f"(Evidence: {result['evidence_found']})")
            print(f"   Grounded: {'✓' if result['grounded'] else '✗'}")
            print(f"   Latency: {result['latency_ms']:.0f}ms | Tokens: {int(result['tokens'])}")
            if result['citations']:
                print(f"   Citations: {len(result['citations'])} chunks from pages "
                      f"{set(c['page'] for c in result['citations'])}")
    
    def save_json(self, filename='eval_results.json'):
        """Save results to JSON file"""
        output = {
            'summary': {
                'total_queries': self.total_queries,
                'retrieval_hit_rate': self.retrieval_hits / self.total_queries,
                'groundedness_rate': self.grounded_answers / self.total_queries,
                'avg_latency_ms': self.total_latency_ms / self.total_queries,
                'total_tokens': int(self.total_tokens),
                'avg_tokens_per_query': int(self.total_tokens / self.total_queries)
            },
            'results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to {filename}")


def run_eval(fixture_path='fixtures/test_document.pdf'):
    """Run evaluation on test cases"""
    print(f"Loading document: {fixture_path}")
    
    # Check if fixture exists
    if not os.path.exists(fixture_path):
        print(f"ERROR: Fixture not found at {fixture_path}")
        print("Please create a fixture PDF first or specify a different path.")
        print("\nTo use the example fixture, first run:")
        print("  python create_fixture_pdf.py")
        return None
    
    # Load document and initialize RAG
    with open(fixture_path, 'rb') as f:
        from werkzeug.datastructures import FileStorage
        file_storage = FileStorage(f, filename=os.path.basename(fixture_path))
        
        try:
            from app.main.llm.document_rag import extract_lcdocs_from_file
            docs = list(extract_lcdocs_from_file(file_storage))
            initialize_qa_rag_chain(docs)
            print(f"Loaded {len(docs)} pages from document\n")
        except Exception as e:
            print(f"ERROR loading document: {e}")
            return None
    
    # Run test cases
    metrics = EvalMetrics()
    
    print("Running evaluation test cases...")
    print("-"*80)
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] {test_case['question']}")
        
        try:
            # Get answer
            result = get_answer_from_rag(test_case['question'], [])
            
            # Get retrieved docs for metrics
            retrieved_docs = RETRIEVER.invoke(test_case['question'])
            
            print(f"  Answer: {result['answer'][:100]}...")
            print(f"  Latency: {result['latency_ms']:.0f}ms | "
                  f"Tokens: {int(result['token_usage']['total_tokens'])}")
            
            metrics.add_result(test_case, result, retrieved_docs)
            
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
    
    return metrics


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Run DocuMate RAG evaluation')
    parser.add_argument('--fixture', default='fixtures/test_document.pdf',
                       help='Path to test PDF fixture')
    parser.add_argument('--output', default='eval_results.json',
                       help='Output JSON file for results')
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    metrics = run_eval(args.fixture)
    
    if metrics:
        metrics.print_summary()
        metrics.save_json(args.output)


if __name__ == '__main__':
    main()
