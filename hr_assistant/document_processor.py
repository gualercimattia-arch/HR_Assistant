import hashlib
import mimetypes
import os
import tempfile
import uuid
from zipfile import ZipFile

from config import Config
from markitdown import MarkItDown
from semantic_chunking import SemanticChunking


class DocumentProcessor:
    SUPPORTED_EXTENSIONS = {
        ".txt": "text",
        ".pdf": "document",
        ".doc": "document",
        ".docx": "document",
        ".ppt": "presentation",
        ".pptx": "presentation",
        ".xls": "spreadsheet",
        ".xlsx": "spreadsheet",
        ".html": "web",
        ".htm": "web",
        ".csv": "data",
        ".json": "data",
        ".xml": "data",
        ".zip": "archive",
    }

    def __init__(self):
        self.md_converter = MarkItDown()
        self.semantic_chunking = SemanticChunking(65, 3)

    @staticmethod
    def get_file_hash(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_document_metadata(self, file_path):
        extension = os.path.splitext(file_path)[1].lower()

        return {
            "hash": self.get_file_hash(file_path),
            "last_modified": os.path.getmtime(file_path),
            "source": os.path.basename(file_path),
            "file_type": self.SUPPORTED_EXTENSIONS.get(extension, "unknown"),
            "mime_type": mimetypes.guess_type(file_path)[0] or "unknown",
            "extension": extension,
        }

    def _convert_to_markdown(self, file_path):
        try:
            return self.md_converter.convert(file_path).text_content
        except Exception as e:
            print(f"Errore nella conversione di {file_path}: {str(e)}")
            return ""

    def _process_zip_file(self, file_path):
        results = []
        with tempfile.TemporaryDirectory() as temp_dir:
            with ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            for root, _, files in os.walk(temp_dir):
                if "__MACOSX" in root:
                    continue

                for file in files:
                    extension = os.path.splitext(file)[1].lower()
                    if extension in self.SUPPORTED_EXTENSIONS:
                        content = self._convert_to_markdown(os.path.join(root, file))
                        if content:
                            results.append((file, content))
        return results

    def read_content(self, file_path):
        extension = os.path.splitext(file_path)[1].lower()
        file_type = self.SUPPORTED_EXTENSIONS.get(extension)

        if not file_type:
            return ""

        if file_type == "archive":
            content = ""
            for filename, zip_content in self._process_zip_file(file_path):
                content += f"\n\nFile: {filename}\n{zip_content}"
            return content

        return self._convert_to_markdown(file_path)

    def read_first_lines(self, file_path, n_lines=100):
        righe = []
        for riga in self.read_content(file_path).splitlines():
            if riga.strip():
                righe.append(riga.strip())
            if len(righe) == n_lines:
                break
        return righe

    def process_single_document(self, file_path):
        documents = []
        metadatas = []
        ids = []

        content = self.read_content(file_path)

        if content:
            chunks = self.semantic_chunking.chunk_text(content)
            file_metadata = self.get_document_metadata(file_path)

            for chunk in chunks:
                if not chunk.isspace() and not chunk == "":
                    documents.append(chunk)
                    metadatas.append(file_metadata)
                    ids.append(str(uuid.uuid4()))

        return documents, metadatas, ids

    def process_documents(self, db):
        current_files = {
            f: self.get_document_metadata(os.path.join(Config.DOCUMENTS_DIR, f))
            for f in os.listdir(Config.DOCUMENTS_DIR)
            if os.path.splitext(f)[1].lower() in self.SUPPORTED_EXTENSIONS
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
                documents, metadatas, ids = self.process_single_document(file_path)

                if action == "update":
                    db.remove_document_by_source(filename)

                if documents:
                    db.add_documents(documents, metadatas, ids)

        for filename in files_to_remove:
            db.remove_document_by_source(filename)

        return len(files_to_add), len(files_to_update), len(files_to_remove)
