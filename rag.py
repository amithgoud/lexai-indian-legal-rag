import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import pickle
import faiss
import numpy as np
from google import genai
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from ddgs import DDGS 
import time

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing or empty. "
        "Please check that your .env file exists in the project root "
        "and contains: GEMINI_API_KEY=your_key_here"
    )
client = genai.Client(api_key=GEMINI_API_KEY)
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
model = SentenceTransformer(EMBEDDING_MODEL)

with open("vector_store/chunks.pkl", "rb") as f:
    data = pickle.load(f)
    chunks = data["chunks"]
    metadata = data["metadata"]
index = faiss.read_index("vector_store/index.faiss")






def search(query,k=3):
    Q= model.encode(QUERY_PREFIX + query)
    Q=np.array([Q]).astype("float32")
    faiss.normalize_L2(Q)
    distances, indices = index.search(Q, k)
    T_chunks=[]
    T_metadata=[]
    T_score=[]
    for i,s in zip(indices[0],distances[0]):
            T_chunks.append(chunks[i])
            T_metadata.append(metadata[i])
            T_score.append(float(s))
    return T_chunks,T_metadata,T_score


def search_web(query):
    web_res=[]
    try:
        fluff_words = ["what", "is", "the", "legal", "status", "of", "in", "are", "how", "to", "?", "under", "arguments", "for"]
        clean_words = [word for word in query.split() if word.lower() not in fluff_words]
        clean_query = " ".join(clean_words)
        legal_query = f"{clean_query} India law site:indiankanoon.org "
        with DDGS() as ddgs:
            result=list(ddgs.text(legal_query,max_results=3))
        for r in result:
            web_res.append(
                {
                    "title":r.get("title",""),
                    "body":r.get("body","")[:400],
                    "url":r.get("href",""),
                    "source_type":"web"
                }
            )
        print(f"web search found {len(web_res)} results")
    except Exception as e:
        print("wen result not  found",e)
    return web_res




def smart_search(question,k=3):
    web_result=[]
    T_c,T_m,T_s=search(question,k)   
    if not T_c:
        avg_score=0
    else:
        avg_score=sum(r for r in T_s)/len(T_c)
    print(f"avg score of the local result  is {avg_score} and the threshold is 0.65")
    if avg_score<0.65:
        web_result=search_web(question)
        return T_c,T_m,T_s,web_result
    else:
        return T_c,T_m,T_s,web_result




    




def generate_answer(question, retrieved_chunks, retrieved_metadata,web_result=[]):
    context = ""
    for i, (chunk, meta) in enumerate(zip(retrieved_chunks, retrieved_metadata)):
        context += f"\n[Source {i+1}: {meta['source']}]\n{chunk}\n"
    if web_result:
        context+="\n the next is web result with its source go through the body of the each search and if any aditional information is needed search its web \n"
        for i,data in enumerate(web_result):
            context+=f"\n[title:{data["title"]},url:{data["url"]}]\n{data["body"]}\n"

    
    prompt = f"""You are an expert Indian legal research assistant for moot court competitions.

RELEVANT LEGAL TEXT:
{context}

QUESTION: {question}

Provide a structured answer with:
## 1. LEGAL ISSUE
## 2. APPLICABLE CONSTITUTIONAL PROVISIONS
## 3. KEY LEGAL PRINCIPLES
## 4. LANDMARK JUDGMENTS & PRECEDENTS
## 5. ARGUMENTS — PETITIONER
## 6. ARGUMENTS — RESPONDENT
## 7. CONCLUSION

Base your answer strictly on the provided legal text."""

# Wait 5 seconds to prevent hitting the Free Tier RPM rate limit
    print("⏳ Pacing API request to avoid rate limits...")
    time.sleep(5)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text

def ask(question):
    print(f"\nSearching for: {question}")
    retrieved_chunks, retrieved_metadata, web_result = smart_search(question)
    print(f"Found {len(retrieved_chunks)} relevant chunks")
    answer = generate_answer(question, retrieved_chunks, retrieved_metadata,web_result)
    return answer


if __name__ == "__main__":
    question = "Scenario: Suppose an autonomous AI system M operates on a formal logical system S. M is tasked with ensuring its own safety by verifying that any code modification M it generates will never produce a unsafe state.The Question: According to Gödel’s Second Incompleteness Theorem, can $M$ formally prove inside system S that M is mathematically guaranteed to be safe and consistent, without invoking a stronger meta-system S? If it cannot, what are the fundamental limits of self-verifying AI alignment?"
    answer = ask(question)
    print("\n" + "="*50)
    print("ANSWER:")
    print("="*50)
    print(answer)
