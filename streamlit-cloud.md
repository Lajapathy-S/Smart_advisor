# Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud (Recommended)

Streamlit Cloud is the easiest and free way to deploy your Streamlit app.

### Step 1: Prepare Your Repository

1. **Ensure your code is on GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

2. **Important files to include:**
   - ✅ `requirements.txt` (must be in root)
   - ✅ `src/frontend/app.py` (main app file)
   - ✅ `config/config.yaml` (configuration)
   - ✅ `data/` directory (sample data)
   - ❌ `.env` file (DO NOT commit - use secrets instead)

### Step 2: Sign Up for Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "Sign up" and authorize with GitHub
3. You'll be redirected to the Streamlit Cloud dashboard

### Step 3: Deploy Your App

1. Click **"New app"** button
2. Fill in the form:
   - **Repository**: Select your GitHub repository
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `src/frontend/app.py`
   - **App URL**: Choose a custom subdomain (optional)
3. Click **"Deploy"**

### Step 4: Configure Secrets

1. In your app's dashboard, go to **Settings** → **Secrets**
2. Add your environment variables:

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
PINECONE_API_KEY = "your-pinecone-key-here"
PINECONE_ENVIRONMENT = "your-pinecone-environment"
VECTOR_DB_TYPE = "CHROMA"
CHROMA_PERSIST_DIR = "./data/chroma_db"
```

3. Click **"Save"**

### Step 5: Your App is Live!

Your app will be available at:
```
https://your-app-name.streamlit.app
```

## Streamlit Cloud Features

✅ **Free tier** includes:
- Unlimited public apps
- 1GB RAM per app
- Automatic HTTPS/SSL
- Custom subdomains
- Automatic deployments on git push

✅ **Automatic updates**: Every time you push to GitHub, your app redeploys

✅ **No credit card required** for free tier

## Troubleshooting

### App won't deploy
- Check that `requirements.txt` is in the root directory
- Verify the main file path is correct: `src/frontend/app.py`
- Check the logs in Streamlit Cloud dashboard

### Import errors
- Ensure all dependencies are in `requirements.txt`
- Check that Python paths are correct
- Verify `src/` directory structure is intact

### API key errors
- Double-check secrets are set correctly
- Ensure no typos in secret names
- Restart the app after adding secrets

### App crashes on startup
- Check logs in Streamlit Cloud dashboard
- Verify vector database initialization (may need to run on first startup)
- Ensure data files are committed to repository

## Advanced Configuration

### Custom Domain (Pro Feature)
- Streamlit Cloud Pro allows custom domains
- Configure in Settings → Custom domain

### Resource Limits
- Free tier: 1GB RAM
- Pro tier: More resources available

### Environment-Specific Configs
You can use different configs for different branches:
- `main` branch → Production
- `dev` branch → Development

## Best Practices

1. **Never commit `.env` files**
   - Use Streamlit Cloud secrets instead
   - Add `.env` to `.gitignore`

2. **Test locally first**
   - Run `streamlit run src/frontend/app.py` locally
   - Fix any issues before deploying

3. **Monitor usage**
   - Check Streamlit Cloud dashboard for usage stats
   - Monitor API usage (OpenAI, Pinecone)

4. **Version control**
   - Use git tags for releases
   - Keep commit messages clear

5. **Error handling**
   - Add try-except blocks in your code
   - Use `st.error()` for user-facing errors

## Example Deployment Workflow

```bash
# 1. Make changes locally
# 2. Test locally
streamlit run src/frontend/app.py

# 3. Commit changes
git add .
git commit -m "Add new feature"

# 4. Push to GitHub
git push origin main

# 5. Streamlit Cloud automatically deploys!
# Check your app URL for updates
```

## Support

- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- Community Forum: https://discuss.streamlit.io/
- GitHub Issues: Report bugs in your repository
