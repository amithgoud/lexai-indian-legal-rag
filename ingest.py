import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import pickle
import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()


DOCUMENTS_FOLDER = "documents"
VECTOR_STORE_FOLDER = "vector_store"
CHUNK_SIZE = 200        # words per chunk
CHUNK_OVERLAP = 50      # overlap between chunks so context isn't lost
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
model = SentenceTransformer(EMBEDDING_MODEL)




def read_pdf(filepath):
    text=""
    reader=PdfReader(filepath)
    for pages in reader.pages:
        extreacted=pages.extract_text()
        if extreacted:
            text+=extreacted+'\n'
    return text



def load_all_documents():
    all_texts = {}
    for filename in os.listdir(DOCUMENTS_FOLDER):
        if filename.endswith(".pdf"):
            filepath = os.path.join(DOCUMENTS_FOLDER, filename)
            print(f"Reading: {filename}")
            text = read_pdf(filepath)
            all_texts[filename] = text
            print(f"  → {len(text)} characters extracted")
    return all_texts




def chunk_text(text, source_name):
    words=text.split()
    chunk=[]
    metadata=[]
    chunk_id=0
    i=0
    while i<len(words):
        if i+CHUNK_SIZE>len(words):
            chunk_words=words[i:]
        else:
            chunk_words=words[i:i+CHUNK_SIZE]
        chunk_str=" ".join(chunk_words)
        chunk.append(chunk_str)
        metadata.append({
            "source": source_name,
            "chunk_id": chunk_id,
            "word_start": i,
            "preview": " ".join(chunk_words[:12]) + "..."
        })


        i+=CHUNK_SIZE-CHUNK_OVERLAP
        chunk_id+=1
    return chunk,metadata




def embed_chunks(chunks):
    print(f"Embedding {len(chunks)} chunks...")
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings



def build_faiss_index(embeddings):
    dimension = embeddings.shape[1]   # 384 for MiniLM
    index = faiss.IndexFlatIP(dimension)  # Inner product = cosine similarity

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings)

    print(f"FAISS index built with {index.ntotal} vectors")
    return index



def save_vector_store(index, all_chunks, all_metadata):
    os.makedirs(VECTOR_STORE_FOLDER, exist_ok=True)

    # Save FAISS index
    faiss.write_index(index, os.path.join(VECTOR_STORE_FOLDER, "index.faiss"))

    # Save chunks and metadata
    with open(os.path.join(VECTOR_STORE_FOLDER, "chunks.pkl"), "wb") as f:
        pickle.dump({"chunks": all_chunks, "metadata": all_metadata}, f)

    print(f"Vector store saved to {VECTOR_STORE_FOLDER}/")




def main():
    print("LEGAL RAG — DOCUMENT INGESTION PIPELINE\n")
    A_chunks=[]
    A_metadata=[]
    doc=load_all_documents()
    if not doc:
        print("mo documents present ")
        return 
    for filename,text in doc.items():
        chunks,metadata=chunk_text(text,filename)
        A_chunks.extend(chunks)
        A_metadata.extend(metadata)
        print(f"{filename}->{len(chunks)}chunks")
    print(f"\n total chunks->{len(A_chunks)}")


    embeddings = embed_chunks(A_chunks)
    embeddings = np.array(embeddings).astype("float32")

    # Build index
    index = build_faiss_index(embeddings)

    # Save
    save_vector_store(index, A_chunks, A_metadata)

    print("\n✅ Ingestion complete!")
    print(f"   Documents processed: {len(doc)}")
    print(f"   Total chunks: {len(A_chunks)}")
    print(f"   Embedding dimensions: {embeddings.shape[1]}")
    print(f"   Ready to search!\n")

if __name__ == "__main__":
    main()

    




    



