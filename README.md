# Clinical QA

Evidence-based answers from ClinicalTrials.gov & PubMed, powered by Claude.

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=your_key_here" > .env
python manage.py runserver 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

## Endpoints

- `POST /api/qa/` — submit a clinical question, get a cited answer
- `GET /api/health/` — health check

## Architecture

1. User question → Claude extracts structured keywords for CT and PubMed
2. ClinicalTrials.gov v2 API + PubMed E-utilities fetched **concurrently**
3. Up to 10 sources (5 CT + 5 PubMed) assembled into context
4. Claude generates a cited answer with inline `[1][2]` references
