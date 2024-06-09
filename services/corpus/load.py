
import llama_index.core
import llama_index.core.node_parser
import llama_index.readers.file

import services.corpus.fs


def load_docs(files: list[str]) -> tuple:
    """
    Load files into docs.
    """
    docs_img = []
    docs_txt = []

    if not files:
        raise ValueError("no files to load")

    files_struct = services.corpus.fs.files_partition(files=files)

    if not files_struct.files_total:
        raise ValueError("no valid files to load")

    if (reader_dir := files_struct.reader_dir):
        reader = llama_index.core.SimpleDirectoryReader(input_files=reader_dir)
        reader_docs = reader.load_data()
        docs_txt.extend(reader_docs)

    if (reader_img := files_struct.reader_img):
        reader = llama_index.core.SimpleDirectoryReader(input_files=reader_img)
        reader_docs = reader.load_data()
        docs_img.extend(reader_docs)

    reader = llama_index.readers.file.PDFReader()
    for file in files_struct.reader_pdf:
        reader_docs = reader.load_data(file)
        docs_txt.extend(reader_docs)

    return (docs_txt, docs_img)


def split_docs(docs: list, splitter: str) -> list:
    """
    Split docs into nodes.
    """
    if splitter == "semantic":
        pass
        # text_splitter = llama_index.core.node_parser.SemanticSplitterNodeParser(
        #     buffer_size=1, breakpoint_percentile_threshold=95, embed_model=model_klass
        # )
    elif splitter.startswith("chunk"):
        _, chunk_size, chunk_overlap = splitter.split(":")
        text_splitter = llama_index.core.node_parser.SentenceSplitter(
            chunk_size=int(chunk_size),
            chunk_overlap=int(chunk_overlap),
        )
    else:
        raise ValueError(f"splitter '{splitter}' invalid")

    return text_splitter.get_nodes_from_documents(docs)
