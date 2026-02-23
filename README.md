# 📸 PhotoSì Price Intelligence Dashboard

## Setup

### 1. Installa dipendenze
```bash
pip install -r requirements.txt
```

### 2. Raccogli i dati (Colab o locale)
Esegui `price_collector.py` per generare `cataloghi_shopping_multi_mercato.csv`

```bash
python price_collector.py
```

### 3. Avvia la dashboard
```bash
streamlit run dashboard.py
```
La dashboard si apre automaticamente su `http://localhost:8501`

---

## Struttura file
```
├── price_collector.py              ← Script raccolta dati (esegui prima)
├── dashboard.py                    ← App Streamlit
├── requirements.txt                ← Dipendenze Python
└── cataloghi_shopping_multi_mercato.csv  ← Output del collector (generato)
```

## Competitor monitorati
🇮🇹 IT · 🇩🇪 DE · 🇫🇷 FR · 🇪🇸 ES · 🇬🇧 GB · 🇳🇱 NL · 🇨🇭 CH

| Competitor | Mercati |
|------------|---------|
| PhotoSì | IT |
| Cewe | IT, DE, FR, ES, GB, NL, CH |
| Photobox | IT, DE, FR, ES, GB |
| Cheerz | IT, FR, ES, GB |
| Pixum | DE, NL |
| Saal Digital | IT, DE, FR, GB |
| Albelli | NL |
| Hofmann | ES |
| Bonusprint | GB |
| Ifolor | CH |
| Lalalab | IT, FR, ES, DE, GB, CH |
| Popsa | GB |
| Journi | DE, GB |
| Once Upon | IT, FR, DE, GB |

## Note valute
- EUR: 1.0 (base)
- GBP: × 1.17
- CHF: × 1.05
