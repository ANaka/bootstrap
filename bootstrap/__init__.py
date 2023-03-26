from pathlib import Path

repo_root = Path(__file__).parent.parent
package_root = Path(__file__).parent
vectorstores_root = package_root / "vectorstores"
langchain_vectorstore_path = vectorstores_root / "langchain.faiss"
