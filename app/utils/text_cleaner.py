"""Text normalization helpers."""
import re

def normalize_text(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[^a-z0-9+#.\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t
from typing import List
import re

def clean_text(text: str) -> str:
    """
    Cleans the input text by removing unnecessary characters and formatting.
    
    Args:
        text (str): The raw text to be cleaned.
        
    Returns:
        str: The cleaned text.
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters (keeping alphanumeric and basic punctuation)
    text = re.sub(r'[^a-zA-Z0-9.,;:()\'"@ ]', '', text)
    return text

def extract_email(text: str) -> List[str]:
    """
    Extracts email addresses from the input text.
    
    Args:
        text (str): The text to search for email addresses.
        
    Returns:
        List[str]: A list of extracted email addresses.
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)

def extract_phone_numbers(text: str) -> List[str]:
    """
    Extracts phone numbers from the input text.
    
    Args:
        text (str): The text to search for phone numbers.
        
    Returns:
        List[str]: A list of extracted phone numbers.
    """
    phone_pattern = r'\+?\d[\d -]{8,}\d'
    return re.findall(phone_pattern, text)

def extract_linkedin_profile(text: str) -> List[str]:
    """
    Extracts LinkedIn profile URLs from the input text.
    
    Args:
        text (str): The text to search for LinkedIn profiles.
        
    Returns:
        List[str]: A list of extracted LinkedIn profile URLs.
    """
    linkedin_pattern = r'(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9-]+'
    return re.findall(linkedin_pattern, text)