"""
Create a fixture PDF for eval testing using PyMuPDF (fitz).
"""
import fitz  # PyMuPDF

def create_fixture_pdf(filename="fixtures/test_document.pdf"):
    """Create a simple test PDF with known content"""
    doc = fitz.open()
    
    # Page 1: Company Information
    page = doc.new_page()
    text = """TechVentures Inc. - Company Overview

TechVentures Inc. is a technology company founded in 2018, specializing in 
artificial intelligence and machine learning solutions. The company is headquartered 
in San Francisco, California, with additional offices in New York and Austin.

The company employs 250 people across its three locations. In 2023, TechVentures 
reported annual revenue of $45 million, representing a 35% year-over-year growth.

TechVentures' mission is to democratize AI technology and make it accessible to 
businesses of all sizes. The company focuses on three core product areas: natural 
language processing, computer vision, and predictive analytics."""
    
    page.insert_text((72, 72), text, fontsize=11, fontname="helv")
    
    # Page 2: Products and Services
    page = doc.new_page()
    text = """Products and Services

TechVentures offers three main products:

1. NLP Suite: A comprehensive natural language processing platform that includes 
   sentiment analysis, entity extraction, and text classification. Pricing starts 
   at $500 per month for the basic tier.

2. VisionAI: An advanced computer vision API supporting object detection, facial 
   recognition, and image classification. The enterprise plan costs $2,000 per month.

3. PredictPro: A predictive analytics tool that helps businesses forecast trends 
   and optimize operations. Custom pricing based on data volume and use case.

All products are available via cloud API or on-premises deployment. The company 
provides 24/7 customer support and maintains a 99.9% uptime SLA."""
    
    page.insert_text((72, 72), text, fontsize=11, fontname="helv")
    
    # Page 3: Team and Leadership
    page = doc.new_page()
    text = """Leadership Team

The TechVentures leadership team brings together expertise from leading technology 
companies and research institutions:

CEO: Dr. Sarah Chen - Previously led AI research at Microsoft for 8 years. PhD in 
Computer Science from Stanford University.

CTO: Michael Rodriguez - Former engineering director at Google. Over 15 years of 
experience building scalable systems.

VP of Product: Jennifer Walsh - Product leader with experience at Amazon and 
startup ventures. MBA from Harvard Business School.

CFO: David Kumar - Financial executive with background in SaaS companies. Previously 
CFO at two successful exits.

The company has raised $30 million in Series B funding, led by Sequoia Capital, 
with participation from Andreessen Horowitz and other prominent venture firms."""
    
    page.insert_text((72, 72), text, fontsize=11, fontname="helv")
    
    doc.save(filename)
    doc.close()
    print(f"Created fixture PDF: {filename}")

if __name__ == "__main__":
    create_fixture_pdf()
