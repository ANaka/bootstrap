import pathlib
import subprocess
import tempfile
import click
from tqdm import tqdm
from langchain.schema import Document as LangChainDocument
from langchain.text_splitter import CharacterTextSplitter
from bootstrap.auth import set_environment_vars
from llama_index import GPTSimpleVectorIndex, Document
from pathlib import Path
from bootstrap import vectorstores_root


REPO_CONFIGS = (
    ('hwchase17', 'langchain'),
    ('jerryjliu', 'llama_index'),
)

def create_llama_index(repo_owner, repo_name, savepath):
    set_environment_vars()
    sources = list(get_github_docs(repo_owner, repo_name))
    docs = [Document.from_langchain_format(doc) for doc in sources]
    index = GPTSimpleVectorIndex(docs)
    if savepath is None:
        savepath = Path(vectorstores_root) / f'github:{repo_name}'
    print(savepath)
    index.save_to_disk(savepath)
    return savepath
    

def get_github_docs(repo_owner, repo_name):
    with tempfile.TemporaryDirectory() as d:
        subprocess.check_call(
            f"git clone --depth 1 https://github.com/{repo_owner}/{repo_name}.git .",
            cwd=d,
            shell=True,
        )
        git_sha = (
            subprocess.check_output("git rev-parse HEAD", shell=True, cwd=d)
            .decode("utf-8")
            .strip()
        )
        repo_path = pathlib.Path(d)
        doc_files = []
        for extension in ['.md', '.mdx', '.ipynb', '.rst']:
            doc_files.extend(list(repo_path.glob(f"**/*{extension}")))
        for doc_file in doc_files:
            with open(doc_file, "r") as f:
                relative_path = doc_file.relative_to(repo_path)
                github_url = f"https://github.com/{repo_owner}/{repo_name}/blob/{git_sha}/{relative_path}"
                yield LangChainDocument(page_content=f.read(), metadata={"source": github_url})

def save_github_indices():
    for repo_owner, repo_name in REPO_CONFIGS:
        savepath = Path(vectorstores_root) / f'github:{repo_name}'
        create_llama_index(repo_owner, repo_name, savepath.as_posix())
        
# dont love the magic paths
def load_langchain_index():
    return GPTSimpleVectorIndex.load_from_disk(Path(vectorstores_root) / f'github:langchain')

def load_llama_index_index():
    return GPTSimpleVectorIndex.load_from_disk(Path(vectorstores_root) / f'github:llama_index')

if __name__ == "__main__":
    save_github_indices()  # This will parse arguments and execute the command.
