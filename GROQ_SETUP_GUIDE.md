# 🚀 Groq AI Setup Guide

## What is Groq?

Groq is a **FREE, FAST, and POWERFUL** AI API that runs on specialized hardware. It's:
- ✅ **Completely FREE** with generous limits (14,400 requests/day)
- ✅ **Super Fast** - Faster than ChatGPT! (~10x faster inference)
- ✅ **High Quality** - Uses Llama 3.1 70B (comparable to GPT-4)
- ✅ **Internet-Connected** - No local installation needed
- ✅ **Easy to Use** - OpenAI-compatible API

---

## 📝 Quick Setup (5 Minutes)

### Step 1: Get Your FREE API Key

1. Visit: **https://console.groq.com**
2. Sign up with Google/GitHub (instant, no credit card needed)
3. Go to "API Keys" section
4. Click "Create API Key"
5. Copy your key (starts with `gsk_...`)

### Step 2: Install Groq Package

Open your terminal and run:

```bash
pip install groq
```

Or use the batch file:

```bash
pip install -r requirements.txt
```

### Step 3: Add API Key to .env File

1. Open (or create) `.env` file in your project root
2. Add this line with your actual API key:

```env
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_key_here
```

**Example:**
```env
AI_PROVIDER=groq
GROQ_API_KEY=gsk_abc123xyz456def789ghi012jkl345mno678pqr901stu234vwx567
```

### Step 4: Test It!

Run the test script to verify everything works:

```bash
python utils/ai_providers.py
```

You should see: `✓ AI Provider Test Successful!`

---

## 🎯 Usage

Your YouTube Shorts generator will now automatically use Groq!

Just run your video generation as normal:

```bash
python start_app.py
```

Or generate multiple videos:

```bash
python generate_5_videos.py
```

---

## 🔄 Switching Between Providers

### Use Groq (Internet, Fast, Free)

In your `.env` file:
```env
AI_PROVIDER=groq
GROQ_API_KEY=your_key_here
```

### Use Ollama (Local, Offline)

In your `.env` file:
```env
AI_PROVIDER=ollama
```

Then make sure Ollama is running:
```bash
ollama serve
```

---

## 📊 Groq Limits (Free Tier)

- **Requests Per Minute (RPM):** 30
- **Requests Per Day (RPD):** 14,400
- **Tokens Per Minute:** 20,000

**This means you can generate:**
- ~30 videos per minute
- ~480 videos per hour
- ~14,400 videos per day

More than enough for most use cases! 🎉

---

## 🆚 Groq vs Ollama Comparison

| Feature | Groq | Ollama |
|---------|------|--------|
| **Cost** | FREE (with limits) | FREE (unlimited) |
| **Speed** | ⚡ Very Fast | 🐌 Slower (depends on GPU) |
| **Quality** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Good |
| **Internet** | ✅ Required | ❌ Not required |
| **Setup** | Easy (just API key) | Complex (model download) |
| **Privacy** | Data sent to cloud | ✅ 100% local |
| **Hardware** | None needed | Requires good GPU/CPU |

---

## 🔧 Troubleshooting

### Error: "GROQ_API_KEY not configured"

**Solution:** Make sure you:
1. Created a `.env` file (not `env.example`)
2. Added `GROQ_API_KEY=your_key_here`
3. Restarted your application

### Error: "Module 'groq' not found"

**Solution:** Install the package:
```bash
pip install groq
```

### Error: "Rate limit exceeded"

**Solution:** You've hit the free tier limits:
- Wait a minute and try again
- Or switch to Ollama for unlimited local generation

### Error: "Invalid API key"

**Solution:** 
1. Check your API key is correct in `.env`
2. Make sure there are no extra spaces
3. Get a new key from https://console.groq.com

---

## 🎨 Available Models

Groq supports several models. To change the model, edit `settings/config.py`:

```python
# Fast and balanced (default)
GROQ_MODEL = "llama-3.1-70b-versatile"

# Even faster, slightly lower quality
GROQ_MODEL = "llama-3.1-8b-instant"

# Alternative model
GROQ_MODEL = "mixtral-8x7b-32768"
```

---

## 💡 Tips

1. **Start with Groq** - It's faster and easier for most users
2. **Fallback works automatically** - If Groq fails, it will try Ollama
3. **Watch your limits** - Free tier is generous but not unlimited
4. **Keep your key safe** - Don't share or commit to Git

---

## 📚 More Information

- **Groq Console:** https://console.groq.com
- **Groq Documentation:** https://console.groq.com/docs
- **Groq Python SDK:** https://github.com/groq/groq-python

---

## ✅ You're All Set!

Your YouTube Shorts generator is now powered by Groq AI! 

Enjoy fast, high-quality script generation! 🎬✨

