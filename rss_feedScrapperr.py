import feedparser
import webbrowser


keywords = [
    "remote sensing",
    "SWOT",
    "dam ",
    "irrigation",
    "land surface model",
    "LSM",
    "modelling",
    "simulation",
    "hydrological model",
    "hydrodynamic model",
    "reservoir",
    "reservoir management",
    "reservoir operation",
    "dam operation",
    "operational scheme",
    "river routing",
    "river regulation",
    "water allocation",
    "water management",
    "anthropogenic impact",
    "hydropower",
    "flood control",
    "multi-purpose reservoir",
    "water balance",
    "groundwater recharge",
    "inundation",
    "storage capacity",
    "satellite altimetry",
    "lake storage",
    "discharge",
    "hydrological forcing",
    "climate forcing",
    "simulation experiment",
    "coupled model",
    "surface water",
    "runoff",
    "evapotranspiration",
    "water resources",
    "large-scale model",
    "GRDC",
    "hydroclimate",
    "grand ensemble",
    "human-water interactions",
    "feedback",
    "SWORD",
    "hydro-informatics"
]

feeds = [
    "https://www.nature.com/nature.rss",
    "https://rss.sciencedirect.com/publication/science/00431354", 
    "https://www.nature.com/npjcleanwater.rss",
    "https://rss.sciencedirect.com/publication/science/22123717",
    "https://rss.sciencedirect.com/publication/science/00221694",
    "https://wires.onlinelibrary.wiley.com/action/showFeed?jc=20491948&type=etoc&feed=rss",
    "https://hess.copernicus.org/articles/xml/rss2_0.xml",
    "https://onlinelibrary.wiley.com/feed/10991085/most-recent",
    "https://journals.ametsoc.org/journalissuetocrss/journals/apme/apme-overview.xml",
    "https://journals.ametsoc.org/journalissuetocrss/journals/aies/aies-overview.xml",
    "https://journals.ametsoc.org/journalissuetocrss/journals/eint/eint-overview.xml", 
    "https://journals.ametsoc.org/journalissuetocrss/journals/hydr/hydr-overview.xml",
    "https://www.tandfonline.com/feed/rss/thsj20",
    "https://iopscience.iop.org/journal/rss/1748-9326",
    "https://www.mdpi.com/rss/journal/water"
]

results = []

for url in feeds:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        # Certains flux n'ont pas 'summary' → prise en compte
        summary = entry.get('summary', '')
        content = entry.title.lower()
        if any(kw in content for kw in keywords):
            results.append({
                "title": entry.title,
                "link": entry.link,
                "summary": summary,
                "source": feed.feed.get('title', url)
            })

# Génération de la page HTML
html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Veille Bibliographique Hydrologie</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f8; color: #333; padding: 30px;}
        h1 { color: #2299e8; }
        .article { background: #fff; border-radius: 10px; box-shadow: 0 2px 6px #ccc4; margin: 20px 0; padding: 20px;}
        .article h2 { margin: 0 0 8px 0; font-size: 1.3em; }
        .article a { color: #0066cc; text-decoration: none;}
        .article a:hover { text-decoration: underline;}
        .article .source { color: #888; font-size: 0.9em; }
        .article .summary { margin: 8px 0 0 0;}
    </style>
</head>
<body>
    <h1>Veille Bibliographique Hydrologie</h1>
"""

if results:
    for article in results:
        html += f"""
        <div class="article">
            <h2><a href="{article['link']}" target="_blank">{article['title']}</a></h2>
            <div class="source">{article['source']}</div>
            <div class="summary">{article['summary']}</div>
        </div>
        """
else:
    html += "<p>Aucun article pertinent trouvé pour cette session.</p>"

html += """
</body>
</html>
"""

# Écriture du fichier HTML
with open("veille.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Page veille.html générée avec succès !")
webbrowser.open_new_tab("veille.html")
