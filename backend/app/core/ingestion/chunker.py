# Imports dependencies.
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        # LangChain's smart splitter tries to keep paragraphs and sentences together
        # chunk_size: How many characters max per chunk?
        # chunk_overlap: How many characters to overlap so we don't accidentally
        #                cut a sentence in half. 
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def chunk_text(self, text: str) -> list[str]:
        """
            Takes a giant wall of text and chops it into a list of smaller, 
            overlapping strings.
        """
        chunks = self.splitter.split_text(text)
        return chunks

# Creating Instance
document_chunker = DocumentChunker()