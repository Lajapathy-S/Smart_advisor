# Deployment Guide

## Option 1: Streamlit Cloud (Recommended - Free & Easy)

Streamlit Cloud is the easiest way to deploy your Streamlit app for free.

### Steps:

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Sign up for Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Sign in with your GitHub account

3. **Deploy your app**
   - Click "New app"
   - Select your repository
   - Set Main file path: `src/frontend/app.py`
   - Click "Deploy"

4. **Configure Secrets**
   - In Streamlit Cloud dashboard, go to Settings → Secrets
   - Add your environment variables:
     ```
     OPENAI_API_KEY=your_key_here
     PINECONE_API_KEY=your_key_here (if using Pinecone)
     PINECONE_ENVIRONMENT=your_env_here
     ```

5. **Your app will be live at**: `https://your-app-name.streamlit.app`

## Option 2: Cloudflare Tunnel (Expose Local App)

Use Cloudflare Tunnel to securely expose your local Streamlit app.

### Steps:

1. **Install Cloudflare Tunnel**
   ```bash
   # Download from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   # Or use Docker
   docker pull cloudflare/cloudflared:latest
   ```

2. **Run your Streamlit app locally**
   ```bash
   streamlit run src/frontend/app.py --server.port 8501
   ```

3. **Create Cloudflare Tunnel**
   ```bash
   cloudflared tunnel --url http://localhost:8501
   ```

4. **Get your public URL**
   - Cloudflare will provide a temporary URL
   - For permanent URL, set up a named tunnel (see Cloudflare docs)

## Option 3: Cloudflare Workers (Limited Python Support)

Note: Cloudflare Workers have limited Python support. Consider using Pyodide or converting to JavaScript.

## Option 4: Other Hosting Options

### Railway
1. Sign up at https://railway.app
2. Connect your GitHub repo
3. Add environment variables
4. Deploy automatically

### Render
1. Sign up at https://render.com
2. Create a new Web Service
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `streamlit run src/frontend/app.py --server.port $PORT`

### Heroku
1. Create `Procfile`:
   ```
   web: streamlit run src/frontend/app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Deploy using Heroku CLI

## Environment Variables for Production

Make sure to set these in your hosting platform:

```
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_key (optional)
PINECONE_ENVIRONMENT=your_pinecone_env (optional)
VECTOR_DB_TYPE=CHROMA
CHROMA_PERSIST_DIR=./data/chroma_db
```

## Pre-deployment Checklist

- [ ] All dependencies in `requirements.txt`
- [ ] Environment variables configured
- [ ] `.env` file NOT committed (in `.gitignore`)
- [ ] Vector database initialized or will be created on first run
- [ ] Tested locally
- [ ] API keys secured (use secrets management)
