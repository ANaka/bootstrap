from langchain import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

from bootstrap.auth import set_environment_vars
from bootstrap.base_prompts import system_prompt

set_environment_vars()


def create_human_message_template():
    return HumanMessagePromptTemplate.from_template("{input}")


def create_chat_prompt(human_message):
    return ChatPromptTemplate.from_messages(
        [system_prompt, MessagesPlaceholder(variable_name="history"), human_message]
    )


def create_conversation_chain(chat_prompt):
    return ConversationChain(
        llm=ChatOpenAI(model_name="gpt-4-0314"),
        prompt=chat_prompt,
        memory=ConversationBufferMemory(return_messages=True),
    )
