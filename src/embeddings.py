import os
from openai import OpenAI

def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is not set. Use the 'key --add' command to set it.")
    return OpenAI(api_key=api_key)

def calculate_embedding(description: str) -> list:
    """
    Calculate embedding vector for a given description using OpenAI's model.
    
    Args:
        description (str): Text to generate embeddings for
        
    Returns:
        list: Embedding vector as a list of floats
    """
    if not description:
        raise ValueError("Description cannot be empty")
    
    client = get_openai_client()
    
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=description
    )
    
    embedding = response.data[0].embedding
    
    return embedding

def similarity_score(embedding1: list, embedding2: list) -> float:
    """
    Calculate cosine similarity between two embedding vectors.
    
    Args:
        embedding1 (list): First embedding vector
        embedding2 (list): Second embedding vector
        
    Returns:
        float: Cosine similarity score (0-1)
    """
    import numpy as np
    
    # Convert to numpy arrays
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    # Calculate cosine similarity
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    return dot_product / (norm1 * norm2)