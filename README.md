# 🍽️ Food Butler — AI Autonomous Ordering Platform

![Food Butler](docs/assets/food_butler_logo.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-%3E%3D0.95-green.svg)](https://fastapi.tiangolo.com/) [![Docker Compose](https://img.shields.io/badge/Docker%20Compose-%3E%3D2-blue.svg)](https://docs.docker.com/compose/)

---

Welcome to Food Butler — a next-generation AI-first food ordering platform that turns natural language into completed orders. This README is long and intentionally detailed: it documents architecture, design principles, the LLM/NLP pipelines, and how to deploy and operate the platform in production or locally.

Table of contents
- [Vision & Elevator Pitch](#vision--elevator-pitch)
- [Why AI-first?](#why-ai-first)
- [Core Capabilities — Quick Highlights](#core-capabilities---quick-highlights)
- [Deep Dive: NLP, LLMs & Autonomous Orchestration](#deep-dive-nlp-llms--autonomous-orchestration)
- [Architecture (Visual + Diagrams)](#architecture-visual--diagrams)
- [Getting Started (Local & Docker)](#getting-started-local--docker)
- [Environment & Secrets](#environment--secrets)
- [Developer Notes & Contributing](#developer-notes--contributing)
- [Publishing & GitHub](#publishing--github)
- [License & Contact](#license--contact)

---

## Vision & Elevator Pitch

Food Butler is an AI-powered culinary concierge: instead of scrolling through menus and tediously assembling a cart, a customer simply speaks or types in natural language. The agent retrieves menu data, filters by dietary preferences and inventory, ranks results, and performs the actions needed (add to cart, checkout) — autonomously when allowed.

Think: "I want the best paneer butter masala under ₹500 near Salt Lake with a delivery ETA under 40 minutes" — Food Butler interprets, searches, scores, and acts.

---

## Why AI-first?

- Removes UI friction: users don't have to browse tens of menus.
- Faster conversions: fewer taps, fewer abandoned carts.
- Personalized suggestions: the agent remembers preferences and context.
- Automation-ready: chain-of-thought + function-calling enables the agent to perform complex flows.

---

## Core Capabilities — Quick Highlights

- Natural language ordering (chat + voice input)
- Autonomous actioning: `add_to_cart`, `checkout_cart`, `modify_order`
- Context-aware search: menu item ranking by price, rating, ETA, and dietary filters
- Inventory-aware menus (out-of-stock items excluded)
- Secure auth with JWT and role-based access (super-admin, restaurant-admin, customer)
- Containerized services (Docker Compose) for reproducible deploys

---

## Deep Dive: NLP, LLMs & Autonomous Orchestration

This section explains the AI brain of Food Butler — important if you want to highlight LLM/NLP capabilities in a portfolio or product listing.

- LLM Backbone: The AI Agent is built as an LLM-first orchestrator. By default the project supports connecting to large LLM providers (Gemini, OpenAI, etc.) using standard API keys. The agent uses function-calling and tool-interfaces to safely control domain actions.
- Intent + Slot Extraction: A light-weight intent classifier extracts user intent (add, search, checkout, cancel) and slot values (dish name, quantity, modifiers, restaurant name). Extracted slots are used to perform precise queries against backend APIs.
- Retrieval & Scoring: To pick the "best" restaurants/items, the agent runs a short RAG-style retrieval across local metadata and performs multi-criteria scoring (price, ETA, rating, dietary matches, past preference). Optionally embeddings are used for semantic menu search.
- Safety & Guardrails: All sensitive or irreversible actions require JWT-scoped permissions. The agent asks for consent before charging or placing the final order unless configured for full autonomy.
- Tooling & Functions: The LLM invokes deterministic tools implemented in `ai_agent/tools.py` such as `get_restaurants`, `get_menu`, `add_to_cart`, `checkout_cart`. Tools return typed outputs so the LLM can plan reliable follow-ups.

Example conversational flow (simplified):

1. User: "Add 2 butter chicken from The Spice Route"
2. Agent: Intent=add; slots={restaurant: "The Spice Route", item: "butter chicken", qty:2}
3. Agent calls `get_menu(restaurant)` → filters by availability + price
4. Agent calls `add_to_cart(item_id, qty)` → tool returns success
5. Agent: "Added 2× Butter Chicken (₹420) to your cart. Checkout now?"

---

## Architecture (Visual + Diagrams)

High-level service map

```text
        ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
        │  Browser UI  │ <---> │  Backend API │ <---> │  PostgreSQL  │
        │ (Chat UI)    │       │  (FastAPI)   │       │   (Storage)   │
        └──────────────┘       └──────────────┘       └──────────────┘
                 ▲                     ▲                     ▲
                 │                     │                     │
                 ▼                     ▼                     ▼
             Voice/STT              AI Orchestrator         Message Queue
             (optional)             (LLM + Tools)           (optional)
```

Service ports (defaults):
- Backend API: `http://localhost:8000`
- AI Agent: `http://localhost:8080`
- Frontend static server: `http://localhost:5500`

---

## Getting Started (Local & Docker)

Quick start (recommended: Docker Compose):

```bash
# from project root
docker compose up --build

# initialize DB (first run)
docker compose exec backend alembic upgrade head
```

Local (dev) with venv:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -r ai_agent/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
uvicorn ai_agent.main_orchestrator:app --reload --port 8080
```

Open the frontend in your browser at `http://localhost:5500` and try the chat interface.

---

## Environment & Secrets

Minimum env variables required (use `.env`):

```env
POSTGRES_DB=food_butler_db
POSTGRES_USER=food_butler_user
POSTGRES_PASSWORD=secret
SECRET_KEY=change_this_to_a_secure_value
GOOGLE_API_KEY=your_gemini_key_or_provider_key
BACKEND_API_URL=http://localhost:8000
```

Never commit `.env` to source control. `.gitignore` is pre-configured.

---

## Developer Notes & Contributing

- Service layout: `backend/` (FastAPI), `ai_agent/` (orchestrator), `frontend/` (static), `tests/` (scripts)
- LLM tools: add new capabilities as deterministic functions in `ai_agent/tools.py` and register them via the orchestrator's function map.
- Migrations: use Alembic in `backend/` for DB schema changes.

Testing

Some tests are scripts designed to run with a live backend and DB. To run isolated unit tests, use `pytest`.

Code style

- Follow PEP8 for Python. Use type hints where helpful. Keep AI tool outputs typed and validated.

Contributing guide

1. Fork the repo
2. Create a feature branch
3. Add tests and update docs
4. Submit a PR and request review

---

## Publishing & GitHub

To publish this repository on GitHub:

```bash
cd main
git remote add origin git@github.com:YOUR_USERNAME/food_butler_llm_based.git
git push -u origin main
```

If you'd like, I can create a GitHub repo and push for you — provide the remote URL or give permission and a token (not via chat; use your local environment). Otherwise run the commands above.

---

## License & Contact

MIT License — see `LICENSE`.

Maintainer: Jaswanth Yamana — please add your contact URL or GitHub profile link here.

---

Enjoy! If you want the README to include additional branded images, color badges, or a GIF demo, tell me which image files to add and I will include them and update the README accordingly.


## Publishing to GitHub

To publish this project to GitHub (or a Microsoft/GitHub organization profile), create a new repository on GitHub and run the following from the project root:

```bash
git init
git add .
git commit -m "chore: initial commit - Food Butler"
git branch -M main
# Use the HTTPS or SSH remote URL provided by GitHub
git remote add origin git@github.com:YOUR_USERNAME/food_butler_llm_based.git
git push -u origin main
```

If you want the repository under a Microsoft organization or profile, create the repo under that account and use the provided remote URL.

Tip: add the `.env` file to `.gitignore` (already included) and **never** push secrets or API keys.
