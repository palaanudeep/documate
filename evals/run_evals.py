#!/usr/bin/env python3
"""
Evaluation harness for DocuMate RAG system.

Runs test questions against PDF and HTML fixtures separately.

Calculates:
- Retrieval hit rate: % of queries where expected evidence is in retrieved chunks
- Groundedness: Basic check that answer contains content from retrieved chunks
- Latency: Average response time
- Token usage: Total tokens consumed

Usage:
    python run_evals.py [--pdf-fixture PATH] [--html-fixture PATH]
"""

import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main.llm.document_rag import (
    initialize_qa_rag_chain, 
    get_answer_from_rag,
    RETRIEVER
)
from test_cases import PDF_TEST_CASES, URL_TEST_CASES


class EvalMetrics:
    def __init__(self, name=""):
        self.name = name
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
            'source_type': test_case.get('source_type', 'unknown'),
            'retrieval_hit': retrieval_hit,
            'grounded': grounded,
            'evidence_found': f"{evidence_found}/{len(expected_evidence)}",
            'latency_ms': result.get('latency_ms', 0),
            'tokens': result.get('token_usage', {}).get('total_tokens', 0),
            'citations': result.get('citations', [])
        })
    
    def print_summary(self, verbose=True):
        """Print evaluation summary"""
        if verbose:
            print("\n" + "="*80)
            print(f"EVALUATION SUMMARY: {self.name}")
            print("="*80)
        
        if self.total_queries == 0:
            print("No queries run")
            return
            
        print(f"Total queries: {self.total_queries}")
        print(f"Retrieval hit rate: {self.retrieval_hits}/{self.total_queries} "
              f"({100*self.retrieval_hits/self.total_queries:.1f}%)")
        print(f"Grounded answers: {self.grounded_answers}/{self.total_queries} "
              f"({100*self.grounded_answers/self.total_queries:.1f}%)")
        print(f"Average latency: {self.total_latency_ms/self.total_queries:.0f}ms")
        print(f"Total tokens used: {int(self.total_tokens)}")
        print(f"Avg tokens per query: {int(self.total_tokens/self.total_queries)}")
        
        if verbose:
            print("="*80)
            
            # Print detailed results
            print("\nDETAILED RESULTS:")
            print("-"*80)
            for i, result in enumerate(self.results, 1):
                print(f"\n{i}. {result['question']}")
                print(f"   Category: {result['category']}, Source: {result['source_type']}")
                print(f"   Retrieval hit: {'✓' if result['retrieval_hit'] else '✗'} "
                      f"(Evidence: {result['evidence_found']})")
                print(f"   Grounded: {'✓' if result['grounded'] else '✗'}")
                print(f"   Latency: {result['latency_ms']:.0f}ms | Tokens: {int(result['tokens'])}")
                if result['citations']:
                    sources_display = []
                    for c in result['citations']:
                        if c.get('source_type') == 'url':
                            sources_display.append(f"URL:{c.get('title', 'N/A')}")
                        else:
                            sources_display.append(f"page {c.get('page', 'N/A')}")
                    print(f"   Citations: {len(result['citations'])} chunks from {', '.join(set(sources_display))}")
    
    def save_json(self, filename='eval_results.json'):
        """Save results to JSON file"""
        output = {
            'summary': {
                'name': self.name,
                'total_queries': self.total_queries,
                'retrieval_hit_rate': self.retrieval_hits / self.total_queries if self.total_queries > 0 else 0,
                'groundedness_rate': self.grounded_answers / self.total_queries if self.total_queries > 0 else 0,
                'avg_latency_ms': self.total_latency_ms / self.total_queries if self.total_queries > 0 else 0,
                'total_tokens': int(self.total_tokens),
                'avg_tokens_per_query': int(self.total_tokens / self.total_queries) if self.total_queries > 0 else 0
            },
            'results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to {filename}")


def load_pdf_fixture(fixture_path):
    """Load PDF fixture and return docs"""
    print(f"Loading PDF: {fixture_path}")
    
    if not os.path.exists(fixture_path):
        print(f"  SKIP: PDF fixture not found")
        return None
    
    with open(fixture_path, 'rb') as f:
        from werkzeug.datastructures import FileStorage
        file_storage = FileStorage(f, filename=os.path.basename(fixture_path))
        
        try:
            from app.main.llm.document_rag import extract_lcdocs_from_file
            docs = list(extract_lcdocs_from_file(file_storage))
            print(f"  Loaded {len(docs)} pages from PDF\n")
            return docs
        except Exception as e:
            print(f"  ERROR loading PDF: {e}")
            return None


def load_html_fixture(fixture_path):
    """Load HTML fixture and return docs with URL metadata"""
    print(f"Loading HTML: {fixture_path}")
    
    if not os.path.exists(fixture_path):
        print(f"  SKIP: HTML fixture not found")
        return None
    
    try:
        # Extract HTML as if it were a URL source
        from bs4 import BeautifulSoup
        import html2text
        from langchain_core.documents import Document
        
        with open(fixture_path, 'r') as f:
            html_content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "CloudTech Solutions"
        
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0
        
        main_content = soup.find('main') or soup.find('body')
        text = h.handle(str(main_content))
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        # Create document with URL-style metadata
        doc = Document(
            page_content=text,
            metadata={
                "source": "file://" + os.path.abspath(fixture_path),
                "source_type": "url",
                "title": title_text,
                "url": "file://" + os.path.abspath(fixture_path),
                "content_length": len(text)
            }
        )
        
        print(f"  Extracted {len(text)} chars from HTML (title: {title_text})\n")
        return [doc]
        
    except Exception as e:
        print(f"  ERROR loading HTML: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_test_suite(test_cases, metrics_name):
    """Run a suite of test cases against loaded RAG system"""
    metrics = EvalMetrics(name=metrics_name)
    
    print(f"Running {len(test_cases)} test cases for {metrics_name}...")
    print("-"*80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] {test_case['question']}")
        
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
    parser.add_argument('--pdf-fixture', default='fixtures/test_document.pdf',
                       help='Path to test PDF fixture')
    parser.add_argument('--html-fixture', default='fixtures/cloudtech_company.html',
                       help='Path to test HTML fixture')
    parser.add_argument('--output', default='eval_results.json',
                       help='Output JSON file for results')
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    all_metrics = []
    
    # Run PDF tests
    if PDF_TEST_CASES:
        pdf_docs = load_pdf_fixture(args.pdf_fixture)
        if pdf_docs:
            initialize_qa_rag_chain(pdf_docs)
            pdf_metrics = run_test_suite(PDF_TEST_CASES, "PDF Tests")
            pdf_metrics.print_summary()
            all_metrics.append(pdf_metrics)
    
    # Run URL tests
    if URL_TEST_CASES:
        html_docs = load_html_fixture(args.html_fixture)
        if html_docs:
            initialize_qa_rag_chain(html_docs)
            url_metrics = run_test_suite(URL_TEST_CASES, "URL Tests")
            url_metrics.print_summary()
            all_metrics.append(url_metrics)
    
    # Combined summary
    if len(all_metrics) > 1:
        print("\n" + "="*80)
        print("COMBINED SUMMARY")
        print("="*80)
        total_queries = sum(m.total_queries for m in all_metrics)
        total_hits = sum(m.retrieval_hits for m in all_metrics)
        total_grounded = sum(m.grounded_answers for m in all_metrics)
        total_latency = sum(m.total_latency_ms for m in all_metrics)
        total_tokens = sum(m.total_tokens for m in all_metrics)
        
        print(f"Total queries: {total_queries} ({PDF_TEST_CASES and len(PDF_TEST_CASES) or 0} PDF, {URL_TEST_CASES and len(URL_TEST_CASES) or 0} URL)")
        print(f"Retrieval hit rate: {total_hits}/{total_queries} ({100*total_hits/total_queries:.1f}%)")
        print(f"Grounded answers: {total_grounded}/{total_queries} ({100*total_grounded/total_queries:.1f}%)")
        print(f"Average latency: {total_latency/total_queries:.0f}ms")
        print(f"Total tokens used: {int(total_tokens)}")
        print(f"Avg tokens per query: {int(total_tokens/total_queries)}")
        print("="*80)
    
    # Save combined results
    if all_metrics:
        combined_results = {
            'pdf': all_metrics[0].results if len(all_metrics) > 0 else [],
            'url': all_metrics[1].results if len(all_metrics) > 1 else [],
            'summary': {
                'total_queries': sum(m.total_queries for m in all_metrics),
                'retrieval_hit_rate': sum(m.retrieval_hits for m in all_metrics) / sum(m.total_queries for m in all_metrics),
                'groundedness_rate': sum(m.grounded_answers for m in all_metrics) / sum(m.total_queries for m in all_metrics),
                'avg_latency_ms': sum(m.total_latency_ms for m in all_metrics) / sum(m.total_queries for m in all_metrics),
                'total_tokens': int(sum(m.total_tokens for m in all_metrics))
            }
        }
        
        with open(args.output, 'w') as f:
            json.dump(combined_results, f, indent=2)
        print(f"\nCombined results saved to {args.output}")


if __name__ == '__main__':
    main()
