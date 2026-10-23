import pandas as df


def dataframe_to_evidence(df):
    if df is None or df.empty:
        return "No matching records were found."

    return df.to_json(
        orient="records",
        force_ascii=False,
        indent=2
    )

def apply_spec(sheets: dict, spec: dict):
    sheet = spec["sheet"]
    if sheet is None:
        raise ValueError("Cannot execute sheet=null.")
    result = sheets[sheet].copy()

    # Add product attributes to variants/reviews so Brand/Category filters work.
    if sheet in ("Variants", "Reviews"):
        product_fields = sheets["Products"][
            ["ProductID", "Brand", "Category", "Subcategory"]
        ].drop_duplicates(subset=["ProductID"])
        result = result.merge(
            product_fields, on="ProductID", how="left",
            validate="many_to_one", suffixes=("", "_product")
        )

    for col, values in spec["ids"].items():
        if not values:
            continue
        if col not in result.columns:
            raise ValueError(
                f"Query supplied {col}, but {sheet} does not contain that ID. "
                "Choose the appropriate sheet or run separate lookups."
            )
        result = result[result[col].astype("string").isin(values)]

    for item in spec["filters"]:
        col, op, value = item["column"], item["op"], item["value"]
        if col not in result.columns:
            raise ValueError(f"Filter column {col!r} is unavailable.")
        series = result[col]
        if op == "eq":
            mask = series == value
        elif op == "ne":
            mask = series != value
        elif op == "in":
            mask = series.isin(value)
        else:
            numeric = df.to_numeric(series, errors="coerce")
            if op == "gt":
                mask = numeric > value
            elif op == "gte":
                mask = numeric >= value
            elif op == "lt":
                mask = numeric < value
            elif op == "lte":
                mask = numeric <= value
            else:
                mask = numeric.between(value[0], value[1])
        result = result[mask.fillna(False)]

    for col, values in spec["text_filters"].items():
        if not values:
            continue
        if col not in result.columns:
            raise ValueError(f"Text filter {col!r} cannot be applied to {sheet}.")
        allowed = {v.strip().casefold() for v in values}
        normalized = result[col].astype("string").str.strip().str.casefold()
        result = result[normalized.isin(allowed)]
    json_result=dataframe_to_evidence(result)
        
 

    has_constraints = (
        any(spec["ids"].values())
        or bool(spec["filters"])
        or any(spec["text_filters"].values())
    )
    if not has_constraints:
        print("\nNo structured constraints; route to text search/RAG.")
    return json_result


