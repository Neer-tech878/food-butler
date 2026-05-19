# 🍽️ Food Butler

**Your AI-powered culinary concierge — order food the way you talk.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-24+-blue.svg)](https://www.docker.com/)

---

## 📋 Table of Contents

- [Project Description](#project-description)
- [Visuals & Architecture](#visuals--architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)
- [Contact & Acknowledgments](#contact--acknowledgments)

---

## Project Description

Food Butler is a full-stack food ordering platform that replaces clunky menus and checkout flows with a natural-language AI agent. Customers simply chat with the butler ("add 2 mutton biryani from Deccan Spice"), and the agent handles restaurant lookup, menu search, cart management, and checkout — autonomously.

### The Problem

Traditional food ordering apps require users to navigate menus, switch between restaurant tabs, and manually build a cart — a friction-heavy experience. This friction leads to **abandoned carts**, **slower checkouts**, and **poor user retention**. Food Butler solves this with a **conversational AI layer** that understands intent, remembers preferences, and acts immediately.

### Core Features

| Feature | Description |
|---|---|
| 🤖 **AI Conversational Ordering** | Chat naturally — the AI parses intent, finds items, and adds them to your cart |
| 📍 **Real-Time Delivery Tracking** | Live order status with map-based delivery updates |
| 👑 **Two-Tier Admin System** | Super Admin manages all restaurants; Restaurant Admins manage their own menus & orders |
| 🧠 **Smart Recommendations** | AI analyzes order history to suggest personalized dishes |
| 📦 **Inventory Management** | Menu items auto-filtered based on live stock levels |
| 🔐 **JWT Authentication** | Secure token-based auth across all services |
| 🛒 **Cart & Checkout** | Full cart lifecycle — add, modify, remove, and checkout |
| 👤 **User Profiles** | Saved addresses and order history for repeat customers |

### Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vanilla JavaScript SPA, HTML5, CSS3 |
| **Backend API** | FastAPI (Python), SQLAlchemy ORM, Alembic migrations |
| **AI Agent** | Google Gemini 2.5 Flash (function calling + automatic tool invocation) |
| **Database** | PostgreSQL 15 |
| **Auth** | JWT (via `python-jose`) + bcrypt password hashing |
| **Containerization** | Docker & Docker Compose |

---

## Visuals & Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Customer Browser                      │
│              frontend/ (Vanilla JS SPA on :5500)             │
└────────────────────────┬────────────────────────────────────┘
                         │  REST / WebSocket
          ┌──────────────┴──────────────┐
          │                             │
  ┌───────▼──────────┐       ┌──────────▼──────────┐
  │  Backend API     │       │   AI Agent           │
  │  FastAPI :8000   │◄──────│   Gemini 2.5 Flash   │
  │  SQLAlchemy ORM  │       │   FastAPI :8080       │
  └───────┬──────────┘       └─────────────────────┘
          │
  ┌───────▼──────────┐
  │  PostgreSQL :5432 │
  │  food_butler_db   │
  └──────────────────┘
```

### Services Overview

1. **Frontend** (`frontend/`) — Customer App, Super Admin panel (`admin.html`), Restaurant Admin panel (`restaurant_admin.html`)
2. **Backend API** (`backend/`) — FastAPI REST API with 10 route modules (auth, menu, cart, orders, delivery, admin, restaurants, customers, inventory, payments)
3. **AI Agent** (`ai_agent/`) — AI orchestrator powered by Gemini 2.5 Flash with automatic function calling (tools: `get_restaurants`, `get_menu`, `add_to_cart`, `checkout_cart`, `get_order_history`, etc.)
4. **Database** — PostgreSQL 15 with full schema managed via Alembic

---

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** v24+ & **Docker Compose** v2+ — [Install Docker](https://docs.docker.com/get-docker/)
- **Google Gemini API Key** — [Get a key from Google AI Studio](https://aistudio.google.com/app/apikey)
- *(Optional)* **Python 3.10+** — only needed if running services locally outside Docker

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JaswanthYamana/food_butler_llm_based.git
   cd food_butler_llm_based
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and fill in your values (see [Usage](#usage) section for required environment variables).

3. **Start all services with Docker Compose:**
   ```bash
   docker compose up --build
   ```
   This automatically starts the **database**, **backend API**, and **AI agent**.

4. **Initialize the database** (first run only):
   ```bash
   docker compose exec backend alembic upgrade head
   python init_database.py
   ```

5. **Access the application:**

   | Interface | URL |
   |---|---|
   | 🛍️ Customer App | http://localhost:5500 |
   | 👑 Super Admin | http://localhost:5500/admin.html |
   | 🏪 Restaurant Admin | http://localhost:5500/restaurant_admin.html |
   | 📡 Backend API Docs | http://localhost:8000/docs |
   | 🤖 AI Agent Health | http://localhost:8080/health |

---

## Usage

### Talking to the AI Butler

Open the Customer App and start a conversation in the chat panel:

```
You:      "Show me what's available at Deccan Spice"
Butler:   Lists menu items from Deccan Spice with prices

You:      "Add 2 mutton biryani from Deccan Spice"
Butler:   ✅ Added 2× Mutton Biryani (₹700) to your cart

You:      "Checkout"
Butler:   🎉 Order placed! Order #12345. Arriving in ~35 minutes.
```

### Running Services

```bash
# Start all services manually (without Docker)
./start_platform.sh

# Stop all services
./stop_services.sh

# Restart the AI agent only
./restart_ai_agent.sh

# Fix 401 authentication issues
./fix_401_and_restart.sh

# View live logs
docker compose logs -f

# View logs for a specific service
docker compose logs -f backend
docker compose logs -f agent
```

### Database Operations

```bash
# Run pending migrations
docker compose exec backend alembic upgrade head

# Create a new migration
docker compose exec backend alembic revision --autogenerate -m "your description"

# Access PostgreSQL shell
docker compose exec db psql -U food_butler_user -d food_butler_db

# Add menu items with stock data
python add_menu_items_with_stock.py

# Check current menu stock
python check_menu_stock.py
```

### Running Tests

```bash
# Test AI authentication end-to-end
./test_ai_auth.sh

# Test all restaurant logins
./test_all_restaurant_logins.sh

# Test menu + stock availability
./test_all_menus_with_stock.sh

# Run Python unit tests
pytest test_*.py -v
```

### Environment Configuration

The following environment variables are required:

```bash
# ─── AI Agent ─────────────────────────────────────
GOOGLE_API_KEY=your_google_gemini_api_key

# ─── PostgreSQL Database ──────────────────────────
POSTGRES_DB=food_butler_db
POSTGRES_USER=food_butler_user
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://food_butler_user:password@localhost/food_butler_db

# ─── JWT Security ─────────────────────────────────
SECRET_KEY=your_64_char_hex_secret_key  # Generate with: openssl rand -hex 32
```

> ⚠️ **Never commit `.env` files to version control.** Add `.env` to your `.gitignore`.

---

## API Reference

The backend exposes a full REST API documented at **http://localhost:8000/docs** (Swagger UI).

### Authentication Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/auth/register` | `POST` | Register a new customer account |
| `/auth/login` | `POST` | Authenticate and receive a JWT token |
| `/auth/refresh` | `POST` | Refresh an expired JWT token |

### Restaurants & Menu Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/restaurants` | `GET` | List all active restaurants |
| `/restaurants/{id}` | `GET` | Get details for a specific restaurant |
| `/menu` | `GET` | List all menu items (supports `restaurant_id` filter) |
| `/menu/{id}` | `GET` | Get a specific menu item |

### Cart & Orders Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/cart` | `GET` | Get the current user's cart |
| `/cart/add` | `POST` | Add an item to the cart |
| `/cart/checkout` | `POST` | Place an order from the current cart |
| `/orders` | `GET` | Get the current user's order history |
| `/orders/{id}` | `GET` | Get details for a specific order |

### Delivery Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/delivery/{order_id}` | `GET` | Get real-time delivery status for an order |
| `/delivery/{order_id}/update` | `PUT` | Update delivery status (restaurant admin) |

### Admin Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/admin/restaurants` | `GET` | List all restaurants (super admin) |
| `/admin/restaurants` | `POST` | Create a new restaurant |
| `/admin/users` | `GET` | List all users (super admin) |
| `/admin/inventory` | `PUT` | Update stock levels |

### AI Agent Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | `GET` | AI agent health check |
| `/chat` | `POST` | Send a message to the AI butler (requires JWT) |
| `/test-auth` | `GET` | Verify JWT authentication is working |

---

## Contributing

We welcome contributions from the community! Here's how to get started:

1. **Fork** the repository and create your feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and write tests where applicable.

3. **Run the test suite** to ensure nothing is broken:
   ```bash
   ./test_ai_auth.sh
   pytest test_*.py -v
   ```

4. **Commit** with a clear, descriptive message:
   ```bash
   git commit -m "feat: add restaurant filtering by cuisine type"
   ```

5. **Open a Pull Request** against the `main` branch with a clear description of your changes.

### Coding Standards

- **Python:** Follow [PEP 8](https://pep8.org/), use type hints where applicable
- **FastAPI Routes:** Keep routers modular (one file per domain in `app/routers/`)
- **AI Tools:** Add new capabilities as wrapped functions in `ai_agent/tools.py`
- **Database:** Always run `alembic revision --autogenerate` after model changes

For detailed contribution guidelines, see [CONTRIBUTING.md](./CONTRIBUTING.md) (if available).

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for full details.

You are free to use, modify, and distribute this software, provided that the original license notice is included. For commercial use, please refer to the license terms.

---

## Contact & Acknowledgments

### Contact

- **Maintainer:** Jaswanth Yamana  
- **Repository:** [github.com/JaswanthYamana/food_butler_llm_based](https://github.com/JaswanthYamana/food_butler_llm_based)  
- **Issues & Feature Requests:** [Open an Issue](https://github.com/JaswanthYamana/food_butler_llm_based/issues)

### Acknowledgments

This project was built on the shoulders of excellent open-source projects:

- [**Google Gemini API**](https://ai.google.dev/) — The intelligence behind the AI Butler, powering natural language understanding and automatic function calling
- [**FastAPI**](https://fastapi.tiangolo.com/) — The high-performance async Python web framework powering both the backend and AI agent
- [**SQLAlchemy**](https://www.sqlalchemy.org/) & [**Alembic**](https://alembic.sqlalchemy.org/) — ORM and database migration tooling
- [**PostgreSQL**](https://www.postgresql.org/) — The reliable relational database storing all platform data
- [**Docker**](https://www.docker.com/) — Containerization making the multi-service setup reproducible and deployable

---

**Built with ❤️ using FastAPI, Google Gemini AI, and PostgreSQL**
# commands
# commands

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
