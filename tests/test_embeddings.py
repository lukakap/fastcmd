import pytest
from unittest.mock import patch, MagicMock

from src.embeddings import calculate_embedding, get_openai_client

class TestEmbeddings:
    
    def test_get_openai_client_with_key(self):
        with patch('os.environ.get', return_value='test-api-key'):
            with patch('src.embeddings.OpenAI') as mock_openai:
                client = get_openai_client()
                mock_openai.assert_called_once_with(api_key='test-api-key')
    
    def test_get_openai_client_without_key(self):
        with patch('os.environ.get', return_value=None):
            with pytest.raises(ValueError) as excinfo:
                get_openai_client()
            assert "OpenAI API key is not set" in str(excinfo.value)
    
    def test_calculate_embedding_empty_description(self):
        with pytest.raises(ValueError) as excinfo:
            calculate_embedding("")
        assert "Description cannot be empty" in str(excinfo.value)
    
    def test_calculate_embedding(self):
        # Mock the OpenAI client and response
        mock_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embedding)]
        
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_response
        
        with patch('src.embeddings.get_openai_client', return_value=mock_client):
            result = calculate_embedding("test description")
            
            # Check if client was called with correct parameters
            mock_client.embeddings.create.assert_called_once_with(
                model="text-embedding-ada-002",
                input="test description"
            )
            
            # Check if result matches expected embedding
            assert result == mock_embedding
