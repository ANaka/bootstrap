import os
import pytest
from unittest.mock import MagicMock, patch
from bootstrap.interface_setup import load_environment_variables, create_human_message_template
from langchain.prompts.chat import HumanMessagePromptTemplate
from bootstrap.interface_setup import create_chat_prompt
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from bootstrap.base_prompts import system_prompt
from bootstrap.interface_setup import create_conversation_chain
from langchain import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

def test_load_environment_variables():
    # Ensure the 'OPENAI_API_KEY' variable is not present before execution
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']

    # Call the load_environment_variables() function
    load_environment_variables()

    # Assert that the 'OPENAI_API_KEY' is present in the environment variables
    assert 'OPENAI_API_KEY' in os.environ

    # Assert that the value of 'OPENAI_API_KEY' is not an empty string
    assert os.environ['OPENAI_API_KEY'] != ""

def test_create_chat_prompt():
    # Define a mock human_message
    mock_human_message = MagicMock(spec=HumanMessagePromptTemplate)

    # Call create_chat_prompt with the mock_human_message
    chat_prompt = create_chat_prompt(mock_human_message)
    
    
