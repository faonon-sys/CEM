# Structured Reasoning System 🧠🔍

## Render Deployment Quick Start 🚀

### Prerequisites
- GitHub Account
- Render Account
- Anthropic/OpenAI API Key

### Deployment Steps
1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure Build Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python backend/main.py`
5. Set Environment Variables:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
   - `LLM_PROVIDER`
   - `DATABASE_URL` (optional, Render PostgreSQL)

### Post-Deployment
- Check application logs
- Verify API endpoints
- Configure additional settings as needed

## Original README Below 👇

[Rest of existing README remains unchanged]