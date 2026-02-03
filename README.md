# 🍍 AlphaSignal 3.0 (Mar-a-Lago Pineapple Index)

A high-frequency investment intelligence system monitoring geopolitical shifts and their impact on the Gold market.

## 🏗️ Architecture

- **Backend (Python)**: Handles intelligence gathering (Google News), AI Analysis (Gemini/DeepSeek), and data persistence (SQLite).
- **Frontend (Next.js 15 & React 19)**: Professional financial dashboard for real-time visualization and backtesting analysis.
- **Database (SQLite)**: Shared source of truth between Python and Node.js.

## 🚀 Getting Started

### 1. Backend Setup
```bash
# Install dependencies
./venv/bin/pip install -r requirements.txt

# Configure environment (IMPORTANT: Never commit .env!)
cp .env.example .env
# Edit .env and fill in your API keys

# Run security check
./scripts/security-check.sh

# Run intelligence engine
./venv/bin/python3 run.py
```

### 2. Frontend Setup
```bash
cd web
npm install
npm run dev
```

### 3. Docker Deployment (Recommended) 🐳
One-command startup for maximum stability:
```bash
# Ensure .env is configured first!
cp .env.example .env

# Start all services (Worker, API, Web)
docker-compose up -d

# View logs
docker-compose logs -f
```
App will be available at: http://localhost:3000

## 🔒 Security

**⚠️ IMPORTANT**: This project uses API keys that must be kept secret!

- ✅ `.env` file is automatically ignored by Git
- ✅ Pre-commit hook prevents accidental commits of sensitive data
- ✅ Run `./scripts/security-check.sh` before pushing

**First-time setup**:
1. Copy `.env.example` to `.env`
2. Get your API keys:
   - Gemini: https://makersuite.google.com/app/apikey
   - DeepSeek: https://platform.deepseek.com/api_keys
3. Fill in `.env` with your actual keys
4. **Never commit `.env` to Git!**

See [SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md) for detailed security practices.

## 📊 The Pineapple Index
- 🍍 **Green Pineapple**: Dovish sentiment, bullish for Gold.
- 🍍 **Red Pineapple**: Hawkish sentiment, bearish for Gold.
- **Backtesting**: System automatically backfills 1h and 24h price movements to calculate win rates and confidence levels.

## 📚 Documentation

- [Project Analysis](docs/PROJECT_ANALYSIS.md) - Comprehensive code review and improvement roadmap
- [Security Guide](docs/SECURITY_GUIDE.md) - Security best practices and emergency response
- [Security Implementation](docs/SECURITY_IMPLEMENTATION.md) - **NEW!** Complete security features guide
- [SSE Upgrade Guide](docs/SSE_UPGRADE_GUIDE.md) - Real-time data streaming architecture
- [Market Data Migration](docs/MARKET_DATA_MIGRATION.md) - Moving to professional data providers
