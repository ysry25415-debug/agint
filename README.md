# Product Hunter AI

**Egyptian Electronics & Gadgets Market Intelligence Platform**

An autonomous AI-powered market research platform for discovering emerging, trending, and potentially profitable electronics and gadgets in the Egyptian market.

## 🚀 Overview

This platform continuously monitors global trends and the Egyptian electronics market to identify profitable opportunities for sourcing and resale.

## 📋 Features

- **Global Product Discovery**: Monitor TikTok, YouTube, Reddit, and other platforms
- **Egyptian Market Research**: Track Amazon EG, Jumia, Noon, and local stores
- **Supplier Discovery**: Find suppliers on Alibaba, 1688, AliExpress, Made-in-China
- **AI-Powered Analysis**: Profit calculations, product scoring, and trend analysis
- **Telegram Alerts**: Daily reports and opportunity notifications
- **Web Dashboard**: Interactive dashboard for market insights

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Product Hunter AI                             │
├───────────────┬───────────────────────────────────────────────────┤
│  Backend      │  Frontend         │  Workers   │  Databases        │
│  (Python       │  (Next.js)        │  (Celery)  │  (PostgreSQL,     │
│   FastAPI)    │                   │            │   Redis)          │
└───────────────┴────────────────────┴────────────┴───────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Python 3.11 + FastAPI
- **Database**: PostgreSQL
- **Queue**: Redis + Celery
- **Frontend**: Next.js 14 + React + TypeScript
- **Automation**: Celery Beat
- **Notifications**: Telegram Bot API
- **Containerization**: Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL
- Redis

### Environment Setup

1. Copy the environment example:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```bash
# Required
POSTGRES_PASSWORD=your_secure_password
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ALERT_CHAT_ID=your_chat_id

# AI Provider
OPENAI_API_KEY=your_openai_api_key
```

### Running Locally

```bash
# Start all services
docker-compose up -d

# Run database migrations
docker-compose run backend python -c "from app.core.database import Base, engine; from app.models.base import *; Base.metadata.create_all(engine)"

# Start the backend
docker-compose run backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start the frontend (in another terminal)
cd frontend && npm install && npm run dev
```

### API Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/products` - List products
- `GET /api/v1/products/search?q=...` - Search products
- `GET /api/v1/sources` - List data sources
- `GET /api/v1/reports/today` - Today's report

## 🧩 Agents

The platform includes these AI agents:

1. **Global Product Discovery Agent** - Monitors global trends
2. **Social Trends Analysis Agent** - Analyzes social media signals
3. **Egyptian Market Research Agent** - Researches local market
4. **Competitor Analysis Agent** - Identifies competitors
5. **Supplier Discovery Agent** - Finds suppliers
6. **Profit Calculation Agent** - Calculates profit margins
7. **Product Scoring Agent** - Scores opportunity potential
8. **Daily Report Generation Agent** - Creates daily reports

## 📊 Scoring System

Products are scored on a 100-point scale:

- **Demand Signals (25%)**: Current demand indicators
- **Market Growth (15%)**: Growth trends
- **Competition (15%)**: Competitive landscape
- **Profit Potential (20%)**: Profit margin potential
- **Sourcing Feasibility (10%)**: Supplier availability
- **Marketing Potential (10%)**: Marketing opportunities
- **Risk & Seasonality (5%)**: Risk factors


## 🗄️ Database Schema

Key tables:
- `products` - Core product information
- `product_variants` - Product variations
- `sources` - Data source tracking
- `source_observations` - Raw data from sources
- `market_prices` - Price history from marketplaces
- `suppliers` - Supplier information
- `supplier_products` - Products from suppliers
- `opportunity_scores` - Scored opportunities
- `daily_reports` - Generated reports
- `agent_executions` - Agent run logs

## 🤖 Source Connectors

The platform includes connectors for:

**Marketplaces (Egyptian)**:
- Amazon Egypt
- Jumia Egypt
- Noon Egypt
- OLX Egypt

**Social Media**:
- TikTok Creative Center
- YouTube
- Reddit
- Meta Ad Library

**Suppliers**:
- Alibaba
- 1688
- AliExpress
- Made-in-China

## 📱 Telegram Bot

Commands:
- `/start` - Initialize bot
- `/today` - View today's report
- `/opportunities` - View top opportunities
- `/product <id>` - View product details

## 🌐 Dashboard

Pages:
- Overview - Key metrics and KPIs
- Top Opportunities - Highest scoring products
- Trending Products - Trending items
- Egyptian Market Analysis - Local market insights
- Global Product Discovery - Global trends
- Supplier Directory - Supplier listings
- Price Tracking - Historical prices
- Product Comparison - Compare products
- Historical Reports - Past reports
- Source Health - Connector status
- Agent Logs - Execution history

## 📝 License

Internal use only.

## 📞 Contact

For questions or support, contact the development team.