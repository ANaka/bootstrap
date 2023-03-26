import os
from unittest.mock import MagicMock

from langchain.prompts.chat import HumanMessagePromptTemplate

from bootstrap.interface_setup import create_chat_prompt, load_environment_variables


def test_load_environment_variables():
    # Ensure the 'OPENAI_API_KEY' variable is not present before execution
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

    # Call the load_environment_variables() function
    load_environment_variables()

    # Assert that the 'OPENAI_API_KEY' is present in the environment variables
    assert "OPENAI_API_KEY" in os.environ

    # Assert that the value of 'OPENAI_API_KEY' is not an empty string
    assert os.environ["OPENAI_API_KEY"] != ""


def test_create_chat_prompt():
    # Define a mock human_message
    mock_human_message = MagicMock(spec=HumanMessagePromptTemplate)

    # Call create_chat_prompt with the mock_human_message
    create_chat_prompt(mock_human_message)
