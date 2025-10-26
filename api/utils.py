def clean_price(price_str: str) -> float:
   
    if not price_str:
        return 0.0
    
    cleaned = "".join(c for c in price_str if c.isdigit() or c == ".")
    try:
        return float(cleaned)
    except ValueError:
        print(f"Não foi possível converter preço: {price_str}")
        return 0.0
