import os
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from odf.opendocument import load
from odf.text import P
from PyPDF2 import PdfReader
import logging

# Set path to Tesseract executable (if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure logging
logging.basicConfig(level=logging.INFO)

def log_extraction(file_path, text):
    """
    Logs details of the file processing.
    """
    logging.info(f"Processed file: {file_path}")
    logging.info(f"Extracted text length: {len(text)} characters")
    if len(text) > 100:  # Log first 100 characters for large texts
        logging.info(f"Extracted text preview: {text[:100]}")
    else:
        logging.info(f"Extracted text preview: {text}")

def extract_data(file_path):
    """
    Extract text from a file based on its type (image, PDF, or ODT).
    """
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower().strip('.')  # Get file extension
    text = "Unsupported file format."
    
    try:
        if file_extension in ['jpg', 'jpeg', 'png']:
            text = extract_text_from_image(file_path)
        elif file_extension == 'pdf':
            text = extract_text_from_pdf(file_path)
        elif file_extension == 'odt':
            text = extract_text_from_odt(file_path)
        else:
            text = "Unsupported file format."
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {str(e)}")
        text = f"Error processing file {file_path}: {str(e)}"

    log_extraction(file_path, text)
    return text

def extract_text_from_image(image_path):
    """
    Extract text from an image file using OCR.
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except FileNotFoundError:
        logging.error(f"File not found: {image_path}")
        return f"Error: File not found {image_path}"
    except Exception as e:
        logging.error(f"Error extracting text from image: {str(e)}")
        return f"Error extracting text from image: {str(e)}"

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using PyPDF2 or OCR as a fallback.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""  # Attempt to extract text

        # If no text is found, fallback to OCR
        if not text.strip():
            pages = convert_from_path(pdf_path, 500)  # Convert to images
            for page in pages:
                text += pytesseract.image_to_string(page)
        return text
    except FileNotFoundError:
        logging.error(f"File not found: {pdf_path}")
        return f"Error: File not found {pdf_path}"
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        return f"Error extracting text from PDF: {str(e)}"

def extract_text_from_odt(odt_path):
    """
    Extract text from an ODT file.
    """
    try:
        doc = load(odt_path)
        text = ""

        for paragraph in doc.getElementsByType(P):
            for node in paragraph.childNodes:
                if node.nodeType == node.TEXT_NODE and node.data.strip():
                    text += node.data.strip() + '\n'

        return text.strip()
    except FileNotFoundError:
        logging.error(f"File not found: {odt_path}")
        return f"Error: File not found {odt_path}"
    except Exception as e:
        logging.error(f"Error extracting text from ODT file: {str(e)}")
        return f"Error extracting text from ODT file: {str(e)}"
