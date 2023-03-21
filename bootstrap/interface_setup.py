from langchain.chat_models import ChatOpenAI
from langchain import ConversationChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder, 
)
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from bootstrap.base_prompts import system_prompt


def load_environment_variables():
    load_dotenv()


def create_human_message_template():
    return HumanMessagePromptTemplate.from_template("{input}")


def create_chat_prompt(human_message):
    return ChatPromptTemplate.from_messages(
        [system_prompt, MessagesPlaceholder(variable_name="history"), human_message]
    )


def create_conversation_chain(chat_prompt):
    return ConversationChain(
        llm=ChatOpenAI(model_name='gpt-4-0314'),
        prompt=chat_prompt,
        memory=ConversationBufferMemory(return_messages=True),
    )
