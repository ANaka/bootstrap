
from llama_index import GPTSimpleVectorIndex, GPTTreeIndex, Document
from pathlib import Path
from typing import Union
from bootstrap import repo_root, vectorstores_root
from bootstrap.introspection import extract_functions_and_classes
import json

def codebase_to_llama_index(root: Union[str, Path] = None,):
    """
    It takes a root directory, recursively extracts all the functions and classes in
    that directory, then creates a hierarchical index of module indices that subsume class/function indices.
    
    :param root: the root of the codebase to index
    :type root: str
    :return: A GPTTreeIndex object
    """
    if root is None:
        root = repo_root
    all_defs = extract_functions_and_classes(root)
    modules = list(set([d['path'] for d in all_defs]))
    indices = []
    for module in modules:
        this_module_defs = [d for d in all_defs if d['path'] == module]
        docs = [Document(json.dumps(d)) for d in this_module_defs]
        index = GPTSimpleVectorIndex(docs)
        summary = index.query(
            "What is a summary of function of this python module?"
        )
        index.set_text(str(summary))
        index.set_doc_id(module)
        indices.append(index)

    tree_index = GPTTreeIndex(indices)
    return tree_index

def save_codebase_llama_index(
    codebase_root: Union[str, Path] = None,
    savepath:Union[str, Path] = None,
    ):
    if codebase_root is None:
        codebase_root = repo_root
        
    index = codebase_to_llama_index(root=codebase_root)
        
    if savepath is None:
        savepath = Path(vectorstores_root) / 'codebase_llama_index'
    
    
    index.save_to_disk(savepath)
    return savepath

def load_codebase_llama_index(savepath:Union[str, Path] = None,):
    if savepath is None:
        savepath = Path(vectorstores_root) / 'codebase_llama_index'
    return GPTTreeIndex.load_from_disk(savepath)