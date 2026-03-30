# Deploy to Streamlit Cloud (Option 1)

Steps to deploy **JSOM Smart Advisor** to **Streamlit Community Cloud** (free).

---

## Step 1: Put your code on GitHub

1. Create a **public** repo on [github.com/new](https://github.com/new) (no need to add a README if you already have one).
2. Push this project:

   ```bash
   cd "c:\LAJA\Semester 3\RPA\PartA_AI_Smart_Advisor"

   git init
   git add .
   git commit -m "Initial commit - JSOM Smart Advisor"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

---

## Step 2: Sign in to Streamlit Cloud

1. Open **[share.streamlit.io](https://share.streamlit.io)**
2. Sign up / sign in with **GitHub** and authorize Streamlit Cloud.

---

## Step 3: Deploy the app

1. Click **New app**.
2. Set:
   - **Repository:** `YOUR_USERNAME/YOUR_REPO_NAME`
   - **Branch:** `main`
   - **Main file path:** `src/frontend/app.py`
3. Click **Deploy**.

---

## Step 4: Secrets (API keys)

The **main app** uses **xAI Grok** — add **`XAI_API_KEY`** in Streamlit **Settings → Secrets**:

```toml
XAI_API_KEY = "xai-your-key-here"
# optional:
XAI_MODEL = "grok-3-mini"
```

Save; the app will restart.

**Optional** — only if you later wire OpenAI-based RAG/embeddings on Cloud:

```toml
OPENAI_API_KEY = "sk-..."
```

Pinecone (optional RAG):

```toml
PINECONE_API_KEY = "..."
PINECONE_ENVIRONMENT = "..."
```

---

## Step 5: Use the app

- URL shape: **`https://your-app-name.streamlit.app`**
- **JSOM Smart Advisor** needs **`XAI_API_KEY`** for recommendations. Live scraping and roadmap JSON fetches do not require OpenAI.

---

## Checklist

- [ ] Code on GitHub (`main`).
- [ ] App main file: **`src/frontend/app.py`**
- [ ] **`XAI_API_KEY`** in **Settings → Secrets**
- [ ] App loads; program + career + resume flow works after key is set

---

## Troubleshooting

| Issue | What to do |
|--------|------------|
| Build fails | Confirm **`requirements.txt`** at repo root and main file path exactly **`src/frontend/app.py`**. |
| Recommendations / LLM errors | Set **`XAI_API_KEY`** (and optional **`XAI_MODEL`**). |
| Import errors | Dependencies in **`requirements.txt`**; push latest code. |
| Slow first load | Free tier cold start; retry after a minute. |

---

## Updating the app

Push to `main`; Streamlit Cloud redeploys automatically.

```bash
git add .
git commit -m "Update app"
git push origin main
```
