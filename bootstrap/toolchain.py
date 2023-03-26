from langchain.agents import Tool
from llama_index.langchain_helpers.agents import IndexToolConfig, LlamaIndexTool
from bootstrap.codebase_index import load_codebase_index
from bootstrap.code_editing import EditorChain
from bootstrap.introspection import (
    get_current_repo_functions_and_classes, 
    get_current_repo_definitions_summary,
    get_source_code,
    edit_source_code,
    )
from bootstrap.github_indices import load_langchain_index, load_llama_index_index

def get_tools():
    return [
        LlamaIndexTool.from_tool_config(
            IndexToolConfig(
            index=load_codebase_index(), 
            name=f"Codebase query",
            description=f"Useful for when you want to answer queries about the current repo. This is the best place to start looking for answers about the codebase.",
            index_query_kwargs={"similarity_top_k": 3},
            tool_kwargs={"return_direct": False}
        )),
        LlamaIndexTool.from_tool_config(
            IndexToolConfig(
            index=load_langchain_index(), 
            name=f"Langchain docs query",
            description=f"Useful for when you want to look up documentation for the langchain library.",
            index_query_kwargs={"similarity_top_k": 3},
            tool_kwargs={"return_direct": False}
        )),
        LlamaIndexTool.from_tool_config(
            IndexToolConfig(
            index=load_llama_index_index(), 
            name=f"llama_index docs query",
            description=f"Useful for when you want to look up documentation for the llama_index library.",
            index_query_kwargs={"similarity_top_k": 3},
            tool_kwargs={"return_direct": False}
        )),
        Tool(
            name="Get repo definitions summary",
            func=get_current_repo_definitions_summary,
            description=get_current_repo_definitions_summary.__doc__,
        ),
        Tool(
            name="Get source code",
            func=get_source_code,
            description=get_source_code.__doc__,
        ),
        
        Tool(
            name='Edit a function/class definition',
            func=EditorChain().run,
            description="Rewrites a piece of source code according to instructions."
        ),
        
    ]