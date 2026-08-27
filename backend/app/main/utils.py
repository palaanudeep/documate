import os
import io
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

from langchain_community.document_loaders.blob_loaders import Blob
from langchain_core.documents import Document

# Configuration
MAX_PAGE_SIZE_MB = 10
REQUEST_TIMEOUT_SECONDS = 30
USER_AGENT = 'DocuMate/1.0 (Research Tool)'

def extract_lcdocs_from_file(file):
    filename = secure_filename(file.filename)
    file_extension = os.path.splitext(filename)[1]

    docs = None
    if file_extension == '.pdf':
        print('PDF FILE')
        # getting lc docs to build rag chain
        docs = langchain_pdf_document_loader(file, filename)
    
    return docs



def langchain_pdf_document_loader(file, filename):
    blob = Blob.from_data(file.stream.read(), path=filename)
    with blob.as_bytes_io() as data:
        doc = fitz.open(stream=data, filetype="pdf")
        yield from [
            Document(page_content=page.get_text(),
                metadata=dict(
                    {
                        "source": blob.source,
                        "file_path": blob.source,
                        "page": page.number,
                        "total_pages": len(doc),
                    },
                    **{
                        k: doc.metadata[k]
                        for k in doc.metadata
                        if type(doc.metadata[k]) in [str, int]
                    },
                ),
            )
            for page in doc
        ]


def extract_lcdocs_from_url(url):
    """
    Fetch and extract text from a URL.
    Returns LangChain Document objects with URL metadata.
    
    Raises:
        ValueError: If URL is invalid, fetch fails, or content is empty/too large
        requests.RequestException: For network/HTTP errors
    """
    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme in ['http', 'https']:
        raise ValueError(f"Invalid URL scheme. Only http/https supported: {url}")
    
    if not parsed.netloc:
        raise ValueError(f"Invalid URL format: {url}")
    
    try:
        # Fetch URL with timeout and size limit
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        response = requests.get(
            url, 
            headers=headers, 
            timeout=REQUEST_TIMEOUT_SECONDS,
            stream=True
        )
        
        # Check status code
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch URL (HTTP {response.status_code}): {url}")
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
            raise ValueError(f"URL does not return HTML content (got {content_type}): {url}")
        
        # Read content with size limit
        content_chunks = []
        total_size = 0
        max_size_bytes = MAX_PAGE_SIZE_MB * 1024 * 1024
        
        for chunk in response.iter_content(chunk_size=8192, decode_unicode=False):
            total_size += len(chunk)
            if total_size > max_size_bytes:
                raise ValueError(f"Page too large (>{MAX_PAGE_SIZE_MB}MB): {url}")
            content_chunks.append(chunk)
        
        html_content = b''.join(content_chunks).decode('utf-8', errors='ignore')
        
        if not html_content.strip():
            raise ValueError(f"Empty content from URL: {url}")
        
        # Parse HTML and extract main text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else parsed.netloc
        
        # Extract main text using html2text for better formatting
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0  # Don't wrap lines
        
        # Try to find main content area
        main_content = (
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', {'class': ['content', 'main', 'article']}) or
            soup.find('body')
        )
        
        if main_content:
            text = h.handle(str(main_content))
        else:
            text = h.handle(html_content)
        
        # Clean up excessive whitespace
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        if not text or len(text) < 100:
            raise ValueError(f"Insufficient text content extracted from URL: {url}")
        
        # Create LangChain Document with URL metadata
        doc = Document(
            page_content=text,
            metadata={
                "source": url,
                "source_type": "url",
                "title": title_text,
                "url": url,
                "content_length": len(text)
            }
        )
        
        return [doc]
        
    except requests.Timeout:
        raise ValueError(f"Request timeout ({REQUEST_TIMEOUT_SECONDS}s) fetching URL: {url}")
    except requests.RequestException as e:
        raise ValueError(f"Network error fetching URL: {url} - {str(e)}")
    except Exception as e:
        # Re-raise ValueError as-is, wrap other exceptions
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error processing URL {url}: {str(e)}")


def extract_lcdocs_from_source(source, source_type='file'):
    """
    Extract LangChain documents from either a file upload or URL.
    
    Args:
        source: File object (for type='file') or URL string (for type='url')
        source_type: 'file' or 'url'
    
    Returns:
        List of LangChain Document objects
    """
    if source_type == 'url':
        return extract_lcdocs_from_url(source)
    elif source_type == 'file':
        return extract_lcdocs_from_file(source)
    else:
        raise ValueError(f"Unknown source_type: {source_type}")