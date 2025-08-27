import pytest
from unittest.mock import MagicMock
from api_client import UniversalAPIClient, APIError

# Fixtures for different API clients
@pytest.fixture
def openai_client():
    return UniversalAPIClient(api_key="fake_key", base_url="https://api.openai.com/v1", api_name="OpenAI")

@pytest.fixture
def anthropic_client():
    return UniversalAPIClient(api_key="fake_key", base_url="https://api.anthropic.com", api_name="Anthropic")

def test_chat_completions_success(openai_client, mocker):
    """Test successful non-streaming API call."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "Hello, world!"}}]}

    mocker.patch("requests.Session.post", return_value=mock_response)

    response = openai_client.chat_completions(messages=[{"role": "user", "content": "Hi"}], model="gpt-4")

    assert response["choices"][0]["message"]["content"] == "Hello, world!"

def test_chat_completions_streaming_success(openai_client, mocker):
    """Test successful streaming API call."""
    stream_data = [
        b'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n',
        b'data: {"choices": [{"delta": {"content": ", "}}]}\n\n',
        b'data: {"choices": [{"delta": {"content": "world!"}}]}\n\n',
        b'data: [DONE]\n\n'
    ]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = stream_data

    mocker.patch("requests.Session.post", return_value=mock_response)

    response_generator = openai_client.chat_completions(messages=[{"role": "user", "content": "Hi"}], model="gpt-4", stream=True)

    chunks = list(response_generator)

    assert len(chunks) == 3
    assert chunks[0]["choices"][0]["delta"]["content"] == "Hello"
    assert chunks[1]["choices"][0]["delta"]["content"] == ", "
    assert chunks[2]["choices"][0]["delta"]["content"] == "world!"

def test_chat_completions_api_error(openai_client, mocker):
    """Test API error handling."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"error": {"message": "Invalid API key"}}

    mocker.patch("requests.Session.post", return_value=mock_response)

    with pytest.raises(APIError) as excinfo:
        openai_client.chat_completions(messages=[{"role": "user", "content": "Hi"}], model="gpt-4")

    assert "Invalid API key" in str(excinfo.value)
    assert excinfo.value.status_code == 401

def test_anthropic_normalization(anthropic_client, mocker):
    """Test normalization of Anthropic's response format."""
    anthropic_response_data = {
        "id": "msg_123",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "Hello from Anthropic"}],
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 10, "output_tokens": 20}
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = anthropic_response_data

    mocker.patch("requests.Session.post", return_value=mock_response)

    response = anthropic_client.chat_completions(messages=[{"role": "user", "content": "Hi"}], model="claude-3")

    # Check if it has been normalized to OpenAI's format
    assert response["choices"][0]["message"]["content"] == "Hello from Anthropic"
    assert response["usage"]["output_tokens"] == 20
