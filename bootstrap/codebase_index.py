
from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader
from pathlib import Path
from typing import Union
from bootstrap import repo_root, vectorstores_root
from bootstrap.auth import set_environment_vars

set_environment_vars()


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
    doc_files = []
    for extension in ['.py', '.toml']:
        doc_files.extend(list(repo_root.glob(f"**/*{extension}")))

    loader = SimpleDirectoryReader(input_files=doc_files)
    documents = loader.load_data()
    return GPTSimpleVectorIndex(documents)


def save_codebase_index(
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

def load_codebase_index(savepath:Union[str, Path] = None,):
    if savepath is None:
        savepath = Path(vectorstores_root) / 'codebase_llama_index'
    return GPTSimpleVectorIndex.load_from_disk(savepath)

if __name__ == "__main__":
    save_codebase_index()