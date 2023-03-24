import pathlib
import subprocess
import tempfile
import click
from tqdm import tqdm
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from bootstrap.interface_setup import load_environment_variables


@click.command()
@click.argument("repo_owner")
@click.argument("repo_name")
@click.argument("index_path")
def create_faiss_index(repo_owner, repo_name, index_path):
    load_environment_variables()
    sources = list(get_github_docs(repo_owner, repo_name))
    source_chunks = []
    splitter = CharacterTextSplitter(separator=" ", chunk_size=1024, chunk_overlap=0)
    for source in tqdm(sources, desc="Processing documents"):
        for chunk in splitter.split_text(source.page_content):
            source_chunks.append(Document(page_content=chunk, metadata=source.metadata))
    search_index = FAISS.from_documents(source_chunks, OpenAIEmbeddings())
    search_index.save_local(index_path)

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
        for extension in ['.md', '.mdx', '.ipynb', '.py', '.rst']:
            doc_files.extend(list(repo_path.glob(f"**/*{extension}")))
        for doc_file in doc_files:
            with open(doc_file, "r") as f:
                relative_path = doc_file.relative_to(repo_path)
                github_url = f"https://github.com/{repo_owner}/{repo_name}/blob/{git_sha}/{relative_path}"
                yield Document(page_content=f.read(), metadata={"source": github_url})

if __name__ == "__main__":
    create_faiss_index()  # This will parse arguments and execute the command.
