import os

from openai import OpenAI


def get_openai_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key is not set. Use the 'key --add' command to set it."
        )
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
        model="text-embedding-ada-002", input=description
    )

    embedding = response.data[0].embedding

    return embedding
