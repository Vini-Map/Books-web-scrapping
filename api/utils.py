def clean_price(price_str: str) -> float:
    if not price_str:
        return 0.0
    return float(price_str.replace("£", "").strip())
