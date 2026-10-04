from .utils import load_products

def by_keyword(keyword):
    k=keyword.strip().upper()
    for p in load_products():
        if p.get("keyword","").upper()==k: return p
    return None
