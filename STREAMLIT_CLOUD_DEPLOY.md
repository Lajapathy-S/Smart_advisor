# Deploy to Streamlit Cloud (Option 1)

Follow these steps to deploy your AI Smart Advisor to **Streamlit Cloud** for free.

---

## Step 1: Put your code on GitHub

1. **Create a new repository** on GitHub:
   - Go to [github.com/new](https://github.com/new)
   - Name it (e.g. `ai-smart-advisor`)
   - Choose **Public**
   - Do **not** add a README (you already have one)
   - Click **Create repository**

2. **Push this project** from your machine:

   ```bash
   cd "c:\LAJA\Semester 3\RPA\PartA_AI_Smart_Advisor"

   git init
   git add .
   git commit -m "Initial commit - AI Smart Advisor"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

   Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub username and repo name.

---

## Step 2: Sign in to Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **Sign up** and sign in with your **GitHub** account
3. Authorize Streamlit Cloud to access your GitHub repos

---

## Step 3: Deploy the app

1. On Streamlit Cloud, click **"New app"**.
2. Fill in:
   - **Repository**: `YOUR_USERNAME/YOUR_REPO_NAME`
   - **Branch**: `main`
   - **Main file path**: `src/frontend/app.py`
   - **App URL** (optional): e.g. `ai-smart-advisor` → your app will be at  
     `https://ai-smart-advisor.streamlit.app`
3. Click **"Deploy"**.

---

## Step 4: Add your secrets (API key)

1. After the app is created, open it and go to the **⋮** menu (top right) → **Settings**.
2. Open the **Secrets** tab.
3. Paste the following and replace the placeholder with your real key:

   ```toml
   OPENAI_API_KEY = "sk-your-openai-api-key-here"
   ```

4. Click **Save**. The app will restart and the **Chat** tab will work once the key is set.

Optional (only if you use Pinecone):

```toml
OPENAI_API_KEY = "sk-..."
PINECONE_API_KEY = "your-pinecone-key"
PINECONE_ENVIRONMENT = "your-pinecone-environment"
```

---

## Step 5: Use your app

- Your app URL will be something like:  
  **`https://your-app-name.streamlit.app`**
- **Degree Plan**, **Career**, and **Skills Analysis** work without any API key.
- **Chat** works after you add `OPENAI_API_KEY` in Secrets.

---

## Checklist

- [ ] Code is on GitHub (main branch).
- [ ] New app created on Streamlit Cloud with main file: `src/frontend/app.py`.
- [ ] `OPENAI_API_KEY` added in **Settings → Secrets**.
- [ ] App loads; Degree Plan / Career / Skills tabs work.
- [ ] After adding the key, Chat tab works.

---

## Troubleshooting

| Issue | What to do |
|--------|------------|
| "App not found" or build fails | Check that **Main file path** is exactly `src/frontend/app.py` and that `requirements.txt` is in the repo root. |
| Chat says add API key | Add `OPENAI_API_KEY` in **Settings → Secrets** and save. |
| Import or module errors | Ensure all dependencies are in `requirements.txt` and that you pushed the latest code. |
| App is slow or times out | Streamlit Cloud free tier has limits; first load after sleep can be slow. |

---

## Updating the app

Push changes to your `main` branch:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Streamlit Cloud will automatically redeploy the app.

---

You’re done. Your app is live on Streamlit Cloud.
