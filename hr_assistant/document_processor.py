import hashlib
import os
import uuid

from config import Config
from semantic_chunking import SemanticChunking


class DocumentProcessor:
    @staticmethod
    def read_first_lines(file_path, n_lines=100):
        righe = []
        with open(file_path, "r", encoding="utf-8") as file:
            for i, riga in enumerate(file):
                if i < n_lines:
                    righe.append(riga.strip())
                else:
                    break
        return righe

    @staticmethod
    def get_file_hash(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def get_document_metadata(file_path):
        return {
            "hash": DocumentProcessor.get_file_hash(file_path),
            "last_modified": os.path.getmtime(file_path),
            "source": os.path.basename(file_path),
        }

    @staticmethod
    def process_single_document(file_path):
        documents = []
        metadatas = []
        ids = []

        with open(file_path, "r", encoding="utf-8") as file:
            chunks = SemanticChunking.chunk_it(file.read())
            file_metadata = DocumentProcessor.get_document_metadata(file_path)

            for chunk in chunks:
                if not chunk.isspace() and not chunk == "":
                    documents.append(chunk)
                    metadatas.append(file_metadata)
                    ids.append(str(uuid.uuid4()))

        return documents, metadatas, ids

    @staticmethod
    def process_documents(db):
        current_files = {
            f: DocumentProcessor.get_document_metadata(
                os.path.join(Config.DOCUMENTS_DIR, f)
            )
            for f in os.listdir(Config.DOCUMENTS_DIR)
            if f.endswith(".txt")
        }

        existing_files = db.get_tracked_files()

        files_to_add = set(current_files.keys()) - set(existing_files.keys())
        files_to_remove = set(existing_files.keys()) - set(current_files.keys())

        files_to_update = {
            f
            for f in set(current_files.keys()) & set(existing_files.keys())
            if current_files[f]["hash"] != existing_files[f]["hash"]
        }

        for action, files in [("add", files_to_add), ("update", files_to_update)]:
            for filename in files:
                file_path = os.path.join(Config.DOCUMENTS_DIR, filename)
                documents, metadatas, ids = DocumentProcessor.process_single_document(
                    file_path
                )

                if action == "update":
                    db.remove_document_by_source(filename)

                if documents:
                    db.add_documents(documents, metadatas, ids)

        for filename in files_to_remove:
            db.remove_document_by_source(filename)

        return len(files_to_add), len(files_to_update), len(files_to_remove)
