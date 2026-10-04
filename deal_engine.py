from datetime import datetime
from .utils import load_products

def score(p):
    discount = float(p.get("discount_percent", 0))
    priority = float(p.get("priority", 0))
    return min(discount, 60) * 1.2 + priority * 0.5

def select(language):
    products = [p for p in load_products() if p.get("active", True)]
    if not products:
        raise RuntimeError("No active products in config/products.json")
    # Stable daily rotation, so the three language posts do not randomly switch products.
    day = datetime.now().date().toordinal()
    ranked = sorted(products, key=lambda p: (-score(p), p["id"]))
    return ranked[day % len(ranked)]
