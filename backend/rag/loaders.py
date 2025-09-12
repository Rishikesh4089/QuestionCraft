import os
from typing import List, Union
import pytesseract
from PIL import Image
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPowerPointLoader
from langchain_core.documents import Document

def load_pdf(file_path: str) -> List[Document]:
    """Loads a PDF file and returns its content as a list of Document objects."""
    loader = PyPDFLoader(file_path)
    return loader.load()

def load_ppt(file_path: str) -> List[Document]:
    """Loads a PowerPoint file and returns its content as a list of Document objects."""
    loader = UnstructuredPowerPointLoader(file_path)
    return loader.load()

def ocr_image(file_path: str) -> List[Document]:
    """Uses Tesseract OCR to extract text from an image file and returns it as a Document."""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return [Document(page_content=text, metadata={"source": file_path})]
    except Exception as e:
        print(f"Error processing image {file_path}: {e}")
        return []

def load_document(file_path: str) -> List[Document]:
    """
    Detects the file type based on its extension and uses the appropriate loader.
    """
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()

    if extension == '.pdf':
        return load_pdf(file_path)
    elif extension in ['.ppt', '.pptx']:
        return load_ppt(file_path)
    elif extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        return ocr_image(file_path)
    else:
        print(f"Warning: Unsupported file type '{extension}' for file: {file_path}")
        return []