import os
import uuid

from config import Config


class DocumentProcessor:
    @staticmethod
    def process_documents():
        documents = []
        metadatas = []
        ids = []

        for filename in os.listdir(Config.DOCUMENTS_DIR):
            if filename.endswith(".txt"):
                with open(os.path.join(Config.DOCUMENTS_DIR, filename), "r", encoding="utf-8") as file:
                    chunks = file.read().replace("\n", ".").split("### ")

                    for chunk in chunks:
                        if not chunk.isspace() and not chunk == "":
                            documents.append(chunk)
                            metadatas.append({"source": filename})
                            ids.append(str(uuid.uuid4()))

        return documents, metadatas, ids

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
