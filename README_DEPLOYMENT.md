# 🚀 Deployment Guide - Cloudflare & Other Options

This guide covers multiple deployment options for your Streamlit AI Smart Advisor app.

## 🎯 Recommended: Streamlit Cloud (Easiest & Free)

**Best for**: Quick deployment, free hosting, automatic updates

See **[streamlit-cloud.md](streamlit-cloud.md)** for detailed instructions.

**Quick steps:**
1. Push code to GitHub
2. Sign up at https://share.streamlit.io/
3. Connect repo and deploy
4. Add secrets for API keys
5. Done! Your app is live

## ☁️ Option 2: Cloudflare Tunnel (Expose Local App)

**Best for**: Exposing local development app securely

See **[cloudflare-tunnel.md](cloudflare-tunnel.md)** for detailed instructions.

**Quick start:**
```bash
# Install cloudflared
# Windows: choco install cloudflared
# Mac: brew install cloudflared

# Run your app locally
streamlit run src/frontend/app.py

# In another terminal, create tunnel
cloudflared tunnel --url http://localhost:8501
```

**Benefits:**
- ✅ Free
- ✅ Automatic HTTPS
- ✅ No port forwarding needed
- ✅ Works behind firewalls

## 🐳 Option 3: Docker Deployment

**Best for**: Containerized deployments, cloud platforms

### Using Docker Compose (Easiest)

```bash
# Set environment variables
export OPENAI_API_KEY=your_key_here

# Start with Docker Compose
docker-compose up -d

# Your app will be at http://localhost:8501
```

### Using Docker directly

```bash
# Build image
docker build -t ai-smart-advisor .

# Run container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/data:/app/data \
  ai-smart-advisor
```

### Deploy Docker to Cloud Platforms

**Railway:**
- Connect GitHub repo
- Railway auto-detects Dockerfile
- Add environment variables
- Deploy!

**Render:**
- Create new Web Service
- Connect GitHub repo
- Set Dockerfile path
- Add environment variables
- Deploy!

**Fly.io:**
```bash
fly launch
fly secrets set OPENAI_API_KEY=your_key
fly deploy
```

## 🚂 Option 4: Railway

**Best for**: Simple cloud deployment with auto-scaling

1. Sign up at https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add environment variables:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY` (optional)
5. Railway auto-detects and deploys!

Configuration file: `railway.json` (already included)

## 🎨 Option 5: Render

**Best for**: Free tier with easy setup

1. Sign up at https://render.com
2. Create new "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run src/frontend/app.py --server.port $PORT --server.address 0.0.0.0`
5. Add environment variables
6. Deploy!

Configuration file: `render.yaml` (already included)

## 🐘 Option 6: Heroku

**Best for**: Traditional PaaS deployment

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set config vars:
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   ```
5. Deploy: `git push heroku main`

Configuration file: `Procfile` (already included)

## 🔧 Environment Variables

All deployment methods require these environment variables:

### Required
- `OPENAI_API_KEY` - Your OpenAI API key

### Optional
- `PINECONE_API_KEY` - If using Pinecone
- `PINECONE_ENVIRONMENT` - Pinecone environment
- `VECTOR_DB_TYPE` - `CHROMA` (default) or `PINECONE`
- `CHROMA_PERSIST_DIR` - Path for ChromaDB (default: `./data/chroma_db`)

## 📋 Pre-Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] `.env` file NOT committed (in `.gitignore`)
- [ ] Environment variables configured in hosting platform
- [ ] Tested locally: `streamlit run src/frontend/app.py`
- [ ] Vector database will initialize on first run (or pre-initialized)

## 🆚 Comparison Table

| Platform | Free Tier | Ease | Auto-Deploy | Best For |
|----------|-----------|------|-------------|----------|
| **Streamlit Cloud** | ✅ Yes | ⭐⭐⭐⭐⭐ | ✅ Yes | Quick deployment |
| **Cloudflare Tunnel** | ✅ Yes | ⭐⭐⭐⭐ | ❌ No | Local dev exposure |
| **Railway** | ⚠️ Limited | ⭐⭐⭐⭐ | ✅ Yes | Simple cloud hosting |
| **Render** | ✅ Yes | ⭐⭐⭐⭐ | ✅ Yes | Free cloud hosting |
| **Heroku** | ❌ No | ⭐⭐⭐ | ✅ Yes | Traditional PaaS |
| **Docker** | ✅ Yes | ⭐⭐⭐ | ⚠️ Manual | Containerized |

## 🎓 Recommended Workflow

1. **Development**: Run locally with `streamlit run src/frontend/app.py`
2. **Testing**: Use Cloudflare Tunnel to share with team
3. **Production**: Deploy to Streamlit Cloud for public access
4. **Scaling**: Move to Railway/Render if needed

## 📚 Additional Resources

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Docker Docs](https://docs.docker.com/)
- [Railway Docs](https://docs.railway.app/)

## 🆘 Troubleshooting

**App won't start:**
- Check environment variables are set
- Verify `requirements.txt` is complete
- Check logs in hosting platform dashboard

**Import errors:**
- Ensure all dependencies in `requirements.txt`
- Check Python version compatibility
- Verify file paths are correct

**API errors:**
- Verify API keys are correct
- Check API quotas/limits
- Ensure keys have proper permissions

**Port issues:**
- Use `$PORT` environment variable for cloud platforms
- Set `--server.address=0.0.0.0` for Docker
- Check firewall settings

Need help? Check the specific deployment guide for your chosen platform!
