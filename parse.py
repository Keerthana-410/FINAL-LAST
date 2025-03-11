import spacy
import re
from langchain_ollama import OllamaLLM

# Load the NLP model for entity recognition
nlp = spacy.load("en_core_web_md")  # Ensure this model is installed

# Initialize Mistral Model
llm = OllamaLLM(model="mistral")

def extract_features(description):
    """Extracts key product specifications from a given description."""
    doc = nlp(description)

    # Extract named entities
    features = [ent.text for ent in doc.ents if ent.label_ in ["PRODUCT", "ORG", "CARDINAL"]]

    # Use regex to extract additional features
    screen_size = re.findall(r"\d+\.\d+-inch", description)  # Matches "6.1-inch"
    mp_values = re.findall(r"\d+MP", description)  # Matches "50MP"
    processor = re.findall(r"Snapdragon \d+ Gen \d+", description)  # Matches "Snapdragon 8 Gen 2"

    # Remove "Snapdragon 8" if "Snapdragon 8 Gen 2" is present
    if any("Snapdragon 8 Gen" in p for p in processor):
        features = [feat for feat in features if feat != "Snapdragon 8"]

    # Combine all extracted features and remove duplicates
    final_features = list(set(features + screen_size + mp_values + processor))

    return final_features

def parse_with_ollama(dom_content, query):
    """Parses the given DOM content based on user instructions using Mistral."""
    try:
        if not dom_content.strip():
            return "⚠️ No content available for extraction."
        
        prompt = f"Extract information based on the following query: {query}\nContent: {dom_content}"
        response = llm.invoke(prompt)
        
        # If the query is about product descriptions, extract features
        if "product" in query.lower():
            features = extract_features(response)
            response += f"\n\n🔍 Extracted Features: {features}"

        return response.strip() if response else "⚠️ No relevant content extracted."
    except Exception as e:
        print(f"❌ [ERROR] Parsing failed: {e}")
        return "Error extracting content. Please try again."

def summarize_with_mistral(dom_content):
    """Generates a summary of the given DOM content using Mistral."""
    try:
        if not dom_content.strip():
            return "⚠️ No content to summarize."
        
        prompt = f"Summarize: {dom_content}"
        response = llm.invoke(prompt)
        return response.strip() if response else "⚠️ No summary generated."
    except Exception as e:
        print(f"❌ [ERROR] Summarization failed: {e}")
        return "Error generating summary. Please try again."
