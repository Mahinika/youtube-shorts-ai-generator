# 🚀 Quick Start: WebUI Integration

## 3-Step Setup

### 1️⃣ Launch the WebUI
```batch
launch_sd_webui.bat
```
Wait for: `Running on local URL: http://127.0.0.1:7860`

### 2️⃣ Test the Integration (Optional)
```batch
python test_sd_webui_integration.py
```

### 3️⃣ Generate YouTube Shorts!
```batch
python start_app.py
```

---

## Already Configured ✅

The integration is **already set up** with optimal settings:

- ✅ Config updated (`SD_METHOD = "webui"`)
- ✅ API client created (`helpers/sd_webui_api.py`)
- ✅ Background generator updated (auto-selects WebUI or diffusers)
- ✅ Launch script created with RTX 2060 optimizations
- ✅ Test script ready

## What You Get

**Before (diffusers):**
- 12-25s per image
- Limited samplers
- Manual model management

**After (WebUI):**
- ⚡ 10-15s per image  
- 🎨 20+ samplers
- 🖼️ Easy model switching via web UI
- 🔧 Extensions support (ControlNet, LoRA, etc.)
- 🔄 Automatic fallback to diffusers

## First Time?

**First run will download ~4GB of models** (10-30 min depending on internet speed)

After that, generation is fast!

## Toggle Between Methods

**Use WebUI** (faster, more features):
```python
# settings/config.py
SD_METHOD = "webui"
```
Then run `launch_sd_webui.bat` before generating

**Use Diffusers** (simpler, no WebUI needed):
```python
# settings/config.py
SD_METHOD = "diffusers"  
```
Just run `start_app.py` directly

---

📖 **Full documentation**: See `STABLE_DIFFUSION_WEBUI_INTEGRATION.md`

🎉 **You're all set!** Just launch the WebUI and start creating!

