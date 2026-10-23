import re
from rank_bm25 import BM25Okapi
from db_connection import retrive_content,retrieve_embedding
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2",local_files_only=False)   # load once at startup

def tokenize(text):
    return re.findall(r"\w+", text.lower())

class BM25Index:
    def __init__(self, ids, texts):
        self.ids = ids
        self.bm25 = BM25Okapi([tokenize(t) for t in texts])

    def search(self, question, k=30):
        scores = self.bm25.get_scores(tokenize(question))
        top = scores.argsort()[::-1][:k]
        return [self.ids[i] for i in top if scores[i] > 0]   # ranked chunk IDs

def rrf(lists, k=60, top=30):
        scores = {}

        for ranked in lists:
            for rank, id_ in enumerate(ranked, 1):
                scores[id_] = scores.get(id_, 0) + 1 / (k + rank)

        ranked_results = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return ranked_results[:top]

def rag(qns):
    rows = retrive_content() #
    index = BM25Index([r[0] for r in rows],
                       [r[1] for r in rows])
    
    bm25_ids = index.search(qns,k=30)

    embed_ids=retrieve_embedding(qns)

    lists=[bm25_ids,embed_ids]
    ranked_results=rrf(lists,top=30)

    text_by_id={row[0]:row[1] for row in rows}

    candidate_ids = [
        chunk_id
        for chunk_id, score in ranked_results
        if chunk_id in text_by_id
    ]
    pairs = [
        (qns, text_by_id[chunk_id])
        for chunk_id in candidate_ids
    ]

    # Step 6: Rerank candidates with CrossEncoder
    scores = reranker.predict(pairs)

    reranked_results = sorted(
        zip(candidate_ids, scores),key=lambda item: item[1],reverse=True)


    top_results = reranked_results[:6]


    context = "\n\n".join(
        f"Source ID: {chunk_id}\n{text_by_id[chunk_id]}"
        for chunk_id, score in top_results
    )

    return context, top_results


  

    

   


   


