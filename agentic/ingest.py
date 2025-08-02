from git import Repo, Blob
from agentic.utils import chunk_code


def get_code_chunks(repo_path: str):
    repo = Repo(repo_path)
    tree = repo.head.commit.tree
    for blob in tree.traverse():
        if isinstance(blob, Blob):
            file_path = str(blob.path)
            if file_path.endswith(".py"):
                raw = blob.data_stream.read()
                code = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
                yield from chunk_code(code, file_path)
