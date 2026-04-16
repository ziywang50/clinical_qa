import httpx
import xml.etree.ElementTree as ET

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
TIMEOUT = 12.0
MAX_CONTENT = 1500


async def fetch_pubmed(keywords: dict) -> list[dict]:
    pm_kw = keywords.get("pubmed", {})
    query = pm_kw.get("query", "")
    date_range = pm_kw.get("date_range")

    esearch_params = {
        "db": "pubmed",
        "term": query,
        "retmax": 5,
        "sort": "relevance",
        "retmode": "json",
    }

    if date_range and ":" in date_range:
        parts = date_range.split(":")
        esearch_params["datetype"] = "pdat"
        esearch_params["mindate"] = parts[0].strip()
        esearch_params["maxdate"] = parts[1].strip()

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            esearch_resp = await client.get(ESEARCH_URL, params=esearch_params)
            esearch_resp.raise_for_status()
            esearch_data = esearch_resp.json()

            pmids = esearch_data.get("esearchresult", {}).get("idlist", [])
            if not pmids:
                return []

            efetch_resp = await client.get(EFETCH_URL, params={
                "db": "pubmed",
                "id": ",".join(pmids),
                "rettype": "abstract",
                "retmode": "xml",
            })
            efetch_resp.raise_for_status()
            xml_text = efetch_resp.text
    except Exception:
        return []

    return _parse_pubmed_xml(xml_text)


def _parse_pubmed_xml(xml_text: str) -> list[dict]:
    results = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    for article in root.findall(".//PubmedArticle"):
        medline = article.find("MedlineCitation")
        if medline is None:
            continue

        pmid_el = medline.find("PMID")
        pmid = pmid_el.text if pmid_el is not None else ""
        if not pmid:
            continue

        article_el = medline.find("Article")
        if article_el is None:
            continue

        title_el = article_el.find("ArticleTitle")
        title = "".join(title_el.itertext()) if title_el is not None else "No title"

        abstract_el = article_el.find("Abstract")
        if abstract_el is None:
            continue
        abstract_parts = []
        for text_el in abstract_el.findall("AbstractText"):
            label = text_el.get("Label")
            text = "".join(text_el.itertext())
            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)
        content = " ".join(abstract_parts)
        if not content.strip():
            continue
        if len(content) > MAX_CONTENT:
            content = content[:MAX_CONTENT]

        results.append({
            "source_type": "pubmed",
            "source_id": pmid,
            "title": title,
            "content": content,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })

    return results
