# ⚡ Groq Quick Start - 2 Minute Setup

## 🚀 Super Fast Setup

### 1️⃣ Get FREE API Key (1 minute)
👉 Visit: **https://console.groq.com**
- Sign up with Google
- Click "Create API Key"
- Copy your key (starts with `gsk_`)

### 2️⃣ Run Setup Script (30 seconds)
```bash
setup_groq.bat
```
Paste your API key when prompted.

### 3️⃣ Generate Videos! (30 seconds)
```bash
python start_app.py
```

**That's it!** 🎉

---

## 🎯 One-Line Commands

**Setup:**
```bash
setup_groq.bat
```

**Generate 1 video:**
```bash
python start_app.py
```

**Generate 5 videos:**
```bash
python generate_5_videos.py
```

**Test connection:**
```bash
python utils/ai_providers.py
```

---

## 🔄 Switch Providers

### Use Groq (Fast, Internet)
Edit `.env`:
```env
AI_PROVIDER=groq
```

### Use Ollama (Local, Offline)
Edit `.env`:
```env
AI_PROVIDER=ollama
```

---

## ❓ Problems?

**"GROQ_API_KEY not set"**
→ Run `setup_groq.bat` again

**"Rate limit exceeded"**
→ Wait 1 minute or switch to Ollama

**"Module 'groq' not found"**
→ Run `pip install groq`

---

## 📊 Why Groq?

✅ **FREE** - 14,400 videos/day  
✅ **FAST** - 10x faster than local AI  
✅ **POWERFUL** - GPT-4 quality  
✅ **EASY** - 2 minute setup  

---

**Full Guide:** See `GROQ_SETUP_GUIDE.md`

**Happy Creating!** 🎬✨

