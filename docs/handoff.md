# ARCHON: LLM Handoff Document

## Project Overview
ARCHON is an enterprise incident intelligence and operational resilience platform built for the All Things Agentic Hackathon (Fortified Enterprise Fleet Track). It orchestrates a 7-agent Google ADK swarm to handle campus-scale physical and operational emergencies with zero knowledge loss.

## Repository Structure
```
archon/
|-- README.md                          # Story-mode README
|-- ARCHITECTURE.md                    # Architecture deep-dive
|-- COMPETITIVE_ANALYSIS.md            # Competitor analysis
|-- LICENSE                            # MIT
|-- docker-compose.yml                 # Local dev
|-- .env.example                       # Environment variables
|-- .gitignore
|-- docs/                              # Comprehensive documentation
|-- backend/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- main.py                        # FastAPI entry point
|   |-- config.py                      # Config & flags
|   |-- agents/                        # 7 ADK agents
|   |-- governance/                    # 7 GEAP governance subsystems
|   |-- tools/                         # 6 specialized tool modules
|   |-- models/                        # Pydantic v2 models
|   |-- services/                      # Firestore, Memory, Gemini
|   |-- api/                           # REST & WebSockets
|   |-- data/                          # Seed datasets
|   |-- tests/                         # 42+ offline tests
|-- frontend/                          # Next.js 14 glassmorphism UI
|-- scripts/                           # Cloud Run & Vertex AI scripts
```

## Critical Rules to Preserve
1. Never stub or simplify logic; every query, filter, and scoring algorithm is fully realized.
2. All 7 GEAP subsystems must remain operational and demonstrable.
3. Keep the no em dashes rule strictly enforced across all documentation and markdown files.
4. All 4 ADK callbacks must remain on every sub-agent in the swarm.
5. Offline test suite (42+ tests) must pass with zero external GCP dependencies.

## Environment Quick Start
```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```
