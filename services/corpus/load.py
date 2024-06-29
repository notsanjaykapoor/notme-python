import csv

import llama_index.core
import llama_index.core.node_parser
import llama_index.readers.file
import uuid

import models
import services.corpus.fs


def load_docs(files: list[str]) -> tuple:
    """
    Load files into docs.
    """
    docs_img = []
    docs_txt = []

    if not files:
        raise ValueError("no files to load")

    files_result = services.corpus.fs.files_partition(files=files)

    if not files_result.files_total:
        raise ValueError("no valid files to load")

    # txt docs
    if (reader_dir := files_result.reader_dir):
        reader = llama_index.core.SimpleDirectoryReader(input_files=reader_dir)
        reader_docs = reader.load_data()
        docs_txt.extend(reader_docs)

    # pdf files
    reader = llama_index.readers.file.PDFReader()
    for file in files_result.reader_pdf:
        reader_docs = reader.load_data(file)
        docs_txt.extend(reader_docs)

    if (reader_idx := files_result.reader_idx):
        # index file with pointers to txt or img files
        img_files = [index_file for index_file in reader_idx if "image" in index_file]
        # txt_files = [index_file for index_file in reader_idx if "image" in index_file]

        for index_file in img_files:
            with open(index_file) as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    caption = row.get("caption") or ""
                    name = row.get("name")
                    uri = row.get("uri") or row.get("url")

                    img_doc = models.NodeImage(
                        caption=caption,
                        id=str(uuid.uuid4()),
                        name=name,
                        uri=uri,
                    )
                    docs_img.append(img_doc)

    return (docs_txt, docs_img)


def split_docs(docs: list, splitter: str) -> list[models.NodeText]:
    """
    Split docs into text nodes.
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

    llama_nodes = text_splitter.get_nodes_from_documents(docs)
    text_nodes = []

    for llama_node in llama_nodes:
        text_node = models.NodeText(
            id=llama_node.node_id,
            file_name=llama_node.metadata.get("file_name"),
            page_label=llama_node.metadata.get("page_label"),
            text=llama_node.text,
        )
        text_nodes.append(text_node)

    return text_nodes
