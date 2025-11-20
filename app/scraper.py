# app/scraper.py
import json
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from app import db
from app.models import Product

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def extract_currency(price_str: str):
    """
    Extrage moneda din stringul original SerpAPI (ex: "$199.99", "€1299", "£899").
    Folosit ca fallback dacă SerpAPI nu ne dă câmpul `currency`.
    """
    if not price_str:
        return None

    mapping = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
        "CHF": "CHF",
        "¥": "JPY",
        "lei": "MDL",
        "lei.": "MDL",
        "RON": "RON",
    }

    for symbol, code in mapping.items():
        if symbol in price_str:
            return code

    return None


def search_product(query: str, page: int = 1, per_page: int = 10) -> list[Product]:
    """
    Caută produse folosind Google Shopping (SerpAPI).
    Nu mai există restricție de țară / domeniu.
    """
    api_key = "ea6b45bcc8887da0b4c0aacb646fde0eea09cc2e950cf21c3408d795abc81bfb"

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
        "hl": "en",
        "num": 100,
    }

    try:
        resp = requests.get("https://serpapi.com/search.json", params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    shopping_results = data.get("shopping_results", [])
    unique_links: set[str] = set()
    items: list[dict] = []

    for item in shopping_results:
        link = item.get("product_link") or item.get("link")
        if not link:
            continue

        if link in unique_links:
            continue
        unique_links.add(link)

        name = item.get("title", "Produs fără nume")

        # preț numeric + valută
        price = item.get("extracted_price")
        currency = item.get("currency") or extract_currency(item.get("price", ""))

        image_url = item.get("thumbnail") or "/static/img/placeholder.png"

        items.append(
            {
                "name": name,
                "price": price,
                "currency": currency,
                "image_url": image_url,
                "link": link,
            }
        )

    # ───── PAGINARE ───────────────────────────────
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = items[start:end]

    added_ids: list[int] = []

    for details in paginated_items:
        link = details["link"]
        name = details["name"]
        price = details["price"]
        currency = details["currency"]
        image_url = details["image_url"]

        existing = db.session.execute(
            db.select(Product).filter_by(link=link)
        ).scalars().first()

        if existing:
            existing.name = name
            if price is not None:
                existing.price = price
            existing.image = image_url
            if currency:
                existing.currency = currency
            if not existing.domain:
                existing.domain = urlparse(link).netloc.replace("www.", "")
            added_ids.append(existing.id)

        else:
            new_product = Product(
                name=name,
                price=price,
                currency=currency,  # salvăm valuta
                image=image_url,
                link=link,
                domain=urlparse(link).netloc.replace("www.", ""),
            )
            db.session.add(new_product)
            db.session.flush()
            added_ids.append(new_product.id)

    db.session.commit()

    if not added_ids:
        return []

    return Product.query.filter(Product.id.in_(added_ids)).all()
