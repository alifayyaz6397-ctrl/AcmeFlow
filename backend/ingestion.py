import re, json, pdfplumber
from google import genai
import os
from dotenv import load_dotenv
from db_connection import store_chunk
load_dotenv()
import time 
from pandas import df 

def embedd_text(docs):
    client=genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=docs
    )
    return result.embeddings[0].values  


path="AcmeFlow_Synthetic_Product_Catalog.xlsx"
Text="find product with id PRD-0003 VAR-00029 HK02022-V03 REV-00028"
Product_IDs=df.read_excel(path,sheet_name="Products")
Variant_IDs=df.read_excel(path,sheet_name="Variants")
Review_IDs=df.read_excel(path,sheet_name="Reviews")
product_list=[]


def embedd_products():
    for i in range(400):
        print(i)
        content = " ".join(Product_IDs.iloc[i].fillna('').astype(str))
        id = Product_IDs.at[i, 'ProductID']
        document="Products"
        time.sleep(2)
        embedding=embedd_text(content)
        store_chunk(id,document,content,embedding)
embedd_products()


def embedd_variants():
    for i in range(1200):
        print(i)
        content = " ".join(Variant_IDs.iloc[i].fillna('').astype(str))
        id = Variant_IDs.at[i,'VariantID']
        document="Variants"
        # time.sleep(1)
        embedding=embedd_text(content)
        store_chunk(id,document,content,embedding)
embedd_variants()


def embedd_review():
    for i in range(1200):
        print(i)
        content = " ".join(Review_IDs.iloc[i].fillna('').astype(str))
        id = Review_IDs.at[i,'ReviewID']
        document="Reviews"
        # time.sleep(1)
        embedding=embedd_text(content)
        store_chunk(id,document,content,embedding)
embedd_review()


HEADER  = re.compile(r"^\s*(DOC-\d{3})\s+[—–-]\s+(.+?)\s*$")
SECTION = re.compile(r"^\s*Section:\s*(.+?)\s*$")
FOOTER  = re.compile(r"^\s*AcmeFlow Expanded Knowledge Base\s+Page\s+\d+\s*$")

def embedd_doc(pdf_path):
    lines, page_of = [], []
    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            for ln in (page.extract_text() or "").splitlines():
                if FOOTER.match(ln):
                    continue
                lines.append(ln); page_of.append(pno)

    docs, cur = [], None
    for ln, pno in zip(lines, page_of):
        m = HEADER.match(ln)
        if m:                                   # new record starts
            cur = {"doc_id": m[1], "title": m[2], "section": None,
                   "content": [], "page": pno}
            docs.append(cur)
            continue
        if cur is None:                         # cover page text
            continue
        s = SECTION.match(ln)
        if s and cur["section"] is None:
            cur["section"] = s[1]
        elif ln.strip():
            cur["content"].append(ln.strip())

    for d in docs:
        d["content"] = " ".join(d["content"])   # re-join wrapped lines
    return docs

docs = embedd_doc("AcmeFlow_Expanded_Knowledge_Base.pdf")
for chunk in range(38):
    print(chunk)
    chunk=docs[chunk]
    time.sleep(2)
    embedding=embedd_text(chunk["content"])
    store_chunk(chunk["doc_id"],chunk["section"],chunk["content"],embedding)
