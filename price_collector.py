"""
competitor_price_collector.py
Script di raccolta prezzi pan-europea via Serper Shopping API.
Salva i risultati in cataloghi_shopping_multi_mercato.csv
"""

import requests
import json
import pandas as pd
import time
import re

# ─────────────────────────────────────────────
# CONFIGURAZIONE
# ─────────────────────────────────────────────
API_KEY = "bf29c15958861346d0c591f195c08321261b9f1f"
SERPER_SHOPPING_URL = "https://google.serper.dev/shopping"

EXCHANGE_RATES = {
    "EUR": 1.0,
    "GBP": 1.17,   # 1 GBP ≈ 1.17 EUR
    "CHF": 1.05,   # 1 CHF ≈ 1.05 EUR
}

# ─────────────────────────────────────────────
# CATALOGO PAN-EUROPEO (EU + UK + CH)
# ─────────────────────────────────────────────
CATALOGHI = [
    # 🇬🇧 REGNO UNITO
    {"competitor": "Photobox",    "paese": "GB", "lingua": "en", "query": "Photobox photo book"},
    {"competitor": "Cewe",        "paese": "GB", "lingua": "en", "query": "Cewe photo book"},
    {"competitor": "Cheerz",      "paese": "GB", "lingua": "en", "query": "Cheerz photo book"},
    {"competitor": "Saal Digital","paese": "GB", "lingua": "en", "query": "Saal Digital photo book"},
    {"competitor": "Bonusprint",  "paese": "GB", "lingua": "en", "query": "Bonusprint photo book"},
    {"competitor": "Lalalab",     "paese": "GB", "lingua": "en", "query": "Lalalab photo book"},
    {"competitor": "Popsa",       "paese": "GB", "lingua": "en", "query": "Popsa photo book"},
    {"competitor": "Journi",      "paese": "GB", "lingua": "en", "query": "Journi photo book"},
    {"competitor": "Once Upon",   "paese": "GB", "lingua": "en", "query": "Once Upon photo book"},

    # 🇩🇪 GERMANIA
    {"competitor": "Cewe",        "paese": "DE", "lingua": "de", "query": "Cewe fotobuch"},
    {"competitor": "Pixum",       "paese": "DE", "lingua": "de", "query": "Pixum fotobuch"},
    {"competitor": "Saal Digital","paese": "DE", "lingua": "de", "query": "Saal Digital fotobuch"},
    {"competitor": "Photobox",    "paese": "DE", "lingua": "de", "query": "Photobox fotobuch"},
    {"competitor": "Lalalab",     "paese": "DE", "lingua": "de", "query": "Lalalab fotobuch"},
    {"competitor": "Journi",      "paese": "DE", "lingua": "de", "query": "Journi fotobuch"},
    {"competitor": "Once Upon",   "paese": "DE", "lingua": "de", "query": "Once Upon fotobuch"},

    # 🇫🇷 FRANCIA
    {"competitor": "Cheerz",      "paese": "FR", "lingua": "fr", "query": "Cheerz livre photo"},
    {"competitor": "Photobox",    "paese": "FR", "lingua": "fr", "query": "Photobox livre photo"},
    {"competitor": "Cewe",        "paese": "FR", "lingua": "fr", "query": "Cewe livre photo"},
    {"competitor": "Saal Digital","paese": "FR", "lingua": "fr", "query": "Saal Digital livre photo"},
    {"competitor": "Lalalab",     "paese": "FR", "lingua": "fr", "query": "Lalalab livre photo"},
    {"competitor": "Once Upon",   "paese": "FR", "lingua": "fr", "query": "Once Upon livre photo"},

    # 🇪🇸 SPAGNA
    {"competitor": "Hofmann",     "paese": "ES", "lingua": "es", "query": "Hofmann album de fotos"},
    {"competitor": "Cheerz",      "paese": "ES", "lingua": "es", "query": "Cheerz album de fotos"},
    {"competitor": "Photobox",    "paese": "ES", "lingua": "es", "query": "Photobox album de fotos"},
    {"competitor": "Cewe",        "paese": "ES", "lingua": "es", "query": "Cewe album de fotos"},
    {"competitor": "Lalalab",     "paese": "ES", "lingua": "es", "query": "Lalalab fotolibro"},

    # 🇮🇹 ITALIA
    {"competitor": "PhotoSì",     "paese": "IT", "lingua": "it", "query": "PhotoSì fotolibro"},
    {"competitor": "Cheerz",      "paese": "IT", "lingua": "it", "query": "Cheerz fotolibro"},
    {"competitor": "Cewe",        "paese": "IT", "lingua": "it", "query": "Cewe fotolibro"},
    {"competitor": "Saal Digital","paese": "IT", "lingua": "it", "query": "Saal Digital fotolibro"},
    {"competitor": "Lalalab",     "paese": "IT", "lingua": "it", "query": "Lalalab fotolibro"},
    {"competitor": "Once Upon",   "paese": "IT", "lingua": "it", "query": "Once Upon fotolibro"},

    # 🇳🇱 OLANDA
    {"competitor": "Albelli",     "paese": "NL", "lingua": "nl", "query": "Albelli fotoboek"},
    {"competitor": "Cewe",        "paese": "NL", "lingua": "nl", "query": "Cewe fotoboek"},
    {"competitor": "Pixum",       "paese": "NL", "lingua": "nl", "query": "Pixum fotoboek"},

    # 🇨🇭 SVIZZERA
    {"competitor": "Cewe",        "paese": "CH", "lingua": "de", "query": "Cewe fotobuch"},
    {"competitor": "Ifolor",      "paese": "CH", "lingua": "de", "query": "Ifolor fotobuch"},
    {"competitor": "Lalalab",     "paese": "CH", "lingua": "fr", "query": "Lalalab livre photo"},
]

# ─────────────────────────────────────────────
# FUNZIONE DI PULIZIA PREZZO
# ─────────────────────────────────────────────
def parse_price(raw: str) -> float | None:
    """Normalizza stringhe prezzo europee/anglosassoni in float."""
    cleaned = re.sub(r"[^\d,\.]", "", str(raw)).strip()
    if not cleaned:
        return None
    try:
        if "," in cleaned and "." in cleaned:
            if cleaned.rfind(",") > cleaned.rfind("."):
                cleaned = cleaned.replace(".", "").replace(",", ".")
            else:
                cleaned = cleaned.replace(",", "")
        elif "," in cleaned:
            cleaned = cleaned.replace(",", ".")
        return float(cleaned)
    except ValueError:
        return None

# ─────────────────────────────────────────────
# RACCOLTA DATI
# ─────────────────────────────────────────────
all_shopping_results = []
print(f"🛒 Avvio estrazione massiva su {len(CATALOGHI)} mercati/competitor...\n")

for item in CATALOGHI:
    payload = json.dumps({
        "q":   item["query"],
        "gl":  item["paese"].lower(),
        "hl":  item["lingua"].lower(),
        "num": 40,
    })
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}

    try:
        print(f"📡 {item['paese']} | {item['competitor']}...")
        resp = requests.post(SERPER_SHOPPING_URL, headers=headers, data=payload, timeout=15)
        resp.raise_for_status()
        shopping = resp.json().get("shopping", [])

        count = 0
        for prod in shopping:
            venditore = str(prod.get("source", "")).lower()
            comp_lower = item["competitor"].lower()

            # Mapping alias competitor → parole chiave nel dominio/venditore
            ALIAS = {
                "onceupon": ["onceupon", "once upon", "once-upon"],
                "journi":   ["journi"],
                "lalalab":  ["lalalab"],
                "popsa":    ["popsa"],
                "photosì":  ["photosi", "photosì", "photosi.it"],
            }
            keywords = ALIAS.get(comp_lower, [comp_lower])
            if not any(k in venditore for k in keywords):
                continue

            valuta   = prod.get("currency", "EUR")
            raw_price = str(prod.get("price", "0"))
            prezzo   = parse_price(raw_price)
            if prezzo is None:
                continue

            tasso = EXCHANGE_RATES.get(valuta, 1.0)

            all_shopping_results.append({
                "mercato":          item["paese"],
                "competitor":       item["competitor"],
                "prodotto":         prod.get("title", ""),
                "prezzo_originale": prezzo,
                "valuta":           valuta,
                "prezzo_eur":       round(prezzo * tasso, 2),
                "link":             prod.get("link", ""),
                "immagine":         prod.get("imageUrl", ""),
                "rating":           prod.get("rating", None),
                "recensioni":       prod.get("ratingCount", None),
            })
            count += 1

        print(f"   ✅ {count} prodotti")

    except Exception as e:
        print(f"   ❌ Errore: {e}")

    time.sleep(1.5)

# ─────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────
if all_shopping_results:
    df = pd.DataFrame(all_shopping_results)
    df.to_csv("cataloghi_shopping_multi_mercato.csv", index=False, encoding="utf-8-sig")
    print(f"\n💾 Salvati {len(df)} prodotti → cataloghi_shopping_multi_mercato.csv")
else:
    print("\n⚠️  Nessun dato raccolto. Controlla la API key e le query.")
