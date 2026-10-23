from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from parse_input import parse_query
from structure_data import apply_spec
from generate_answer import generate_response
from rag_data import rag
from render_markdown import markdown_to_text

load_dotenv()

app = FastAPI(title="AcmeFlow API", version="1.0.0")


BASE_DIR = Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR / "AcmeFlow_Synthetic_Product_Catalog.xlsx"


class Question(BaseModel):
    query: str



@app.on_event("startup")
def load_catalog():
    global sheets

    if not EXCEL_PATH.exists():
        raise RuntimeError(f"Excel file not found: {EXCEL_PATH}")

    sheets = {
        "Products": pd.read_excel(EXCEL_PATH, sheet_name="Products"),
        "Variants": pd.read_excel(EXCEL_PATH, sheet_name="Variants"),
        "Reviews": pd.read_excel(EXCEL_PATH, sheet_name="Reviews"),
    }


@app.get("/")
def home():
    return {"message": "AcmeFlow API is running"}


@app.post("/api/")
def generate(qns: Question):
    try:
        json_query = parse_query(qns.query)
        route = json_query["route"]
        result = []

        if route == "structured":
            structure_result = apply_spec(sheets, json_query["query"])
            result.append(structure_result)

        elif route == "rag":
            rag_result = rag(qns.query)
            result.append(rag_result)

        elif route == "hybrid":
            structure_result = apply_spec(sheets, json_query["query"])
            rag_result = rag(qns.query)
            result.extend([structure_result, rag_result])

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported route: {route}",
            )

        answer = generate_response(qns.query, result, route)
        return {"answer": markdown_to_text(answer)}

    except HTTPException:
        raise
    except Exception as exc:
        print(f"Request failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question.",
        ) from exc
