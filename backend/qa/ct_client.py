import httpx

CT_BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
TIMEOUT = 12.0
MAX_CONTENT = 1500


async def fetch_clinical_trials(keywords: dict) -> list[dict]:
    ct_kw = keywords.get("clinicaltrials", {})

    params = {
        "query.term": ct_kw.get("query", ""),
        "fields": "NCTId,BriefTitle,BriefSummary,Condition,Phase,OverallStatus,StartDate,LeadSponsorName",
        "pageSize": 5,
        "format": "json",
    }

    if ct_kw.get("condition"):
        params["query.cond"] = ct_kw["condition"]
    #Fixed: deleted filter.phase(not in documentation
    #if ct_kw.get("phase"):
    #    params["filter.phase"] = ct_kw["phase"]
    query = ct_kw.get("query", "")
    if ct_kw.get("phase"):
        query += f" {ct_kw['phase']}"
    params["query.term"] = query
    VALID_STATUSES = {"RECRUITING", "COMPLETED", "ACTIVE_NOT_RECRUITING", 
                  "NOT_YET_RECRUITING", "TERMINATED", "SUSPENDED", "WITHDRAWN"} #Added safety check
    if ct_kw.get("status") in VALID_STATUSES:
        params["filter.overallStatus"] = ct_kw["status"]

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(CT_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        print(f"CT API ERROR: {e}")   #Added Error Handling
        return []

    studies = data.get("studies", [])
    results = []

    for study in studies:
        proto = study.get("protocolSection", {})
        id_module = proto.get("identificationModule", {})
        desc_module = proto.get("descriptionModule", {})
        status_module = proto.get("statusModule", {})
        design_module = proto.get("designModule", {})

        nct_id = id_module.get("nctId", "")
        if not nct_id:
            continue

        title = id_module.get("briefTitle", "No title")
        summary = desc_module.get("briefSummary", "")
        if len(summary) > MAX_CONTENT:
            summary = summary[:MAX_CONTENT]

        results.append({
            "source_type": "clinicaltrials",
            "source_id": nct_id,
            "title": title,
            "content": summary,
            "phase": str(design_module.get("phaseList", {}).get("phase", [""])),
            "status": status_module.get("overallStatus", ""),
            "url": f"https://clinicaltrials.gov/study/{nct_id}",
        })
    if not results:
        print("ZERO: No clinical trials found for query: {ct_kw.get('query', '')}")
    else:
        print(len(results))
    return results
