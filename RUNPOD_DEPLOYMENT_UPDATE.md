# RunPod Deployment Update Guide - TorchVision Fix

## 🚨 Issue Identified
From `My Pods Logs (27).txt`, the RunPod container is missing the new TorchVision fix files:
```
python3: can't open file '/workspace/start_fastapi_with_fix.py': [Errno 2] No such file or directory
```

## ✅ Solution: Update Container with Latest Fixes

You have **3 options** to get the TorchVision fixes into your RunPod container:

---

## 🚀 Option 1: Quick Fix - Manual File Copy (RECOMMENDED)

**Fastest solution** - Copy the missing files directly to your running container:

### Step 1: Connect to your RunPod container via SSH
```bash
# Use the SSH command from your RunPod interface
ssh root@<your-pod-ip>
```

### Step 2: Navigate to workspace and pull latest code
```bash
cd /workspace
git fetch origin
git checkout wan2gp
git pull origin wan2gp
```

### Step 3: Verify the new files are present
```bash
ls -la start_fastapi_with_fix.py
ls -la test_torchvision_circular_import_fix.py
ls -la TORCHVISION_CIRCULAR_IMPORT_FIX.md
```

### Step 4: Test the fix
```bash
python3 test_torchvision_circular_import_fix.py
```

### Step 5: Restart the web demo
```bash
bash run_web_demo.sh
```

---

## 🐳 Option 2: Rebuild Docker Image (PERMANENT SOLUTION)

**Best long-term solution** - Rebuild the Docker image with all fixes:

### Step 1: Build new Docker image locally
```bash
# From your local machine (in the project directory)
docker build -t thanveerdev/hunyuan-video-avatar:wan2gp .
```

### Step 2: Push to Docker Hub
```bash
docker push thanveerdev/hunyuan-video-avatar:wan2gp
```

### Step 3: Update RunPod template
Update your `runpod_template.json`:
```json
{
  "dockerImage": "thanveerdev/hunyuan-video-avatar:wan2gp",
  "imageName": "thanveerdev/hunyuan-video-avatar:wan2gp"
}
```

### Step 4: Deploy new RunPod instance
- Stop current pod
- Create new pod with updated template
- The new container will have all TorchVision fixes included

---

## 🔧 Option 3: Alternative Docker Build Commands

If you prefer different tagging:

### Build and tag as latest
```bash
docker build -t thanveerdev/hunyuan-video-avatar:latest .
docker push thanveerdev/hunyuan-video-avatar:latest
```

### Build with specific fix tag
```bash
docker build -t thanveerdev/hunyuan-video-avatar:torchvision-fix .
docker push thanveerdev/hunyuan-video-avatar:torchvision-fix
```

---

## 🧪 Verification Steps

After applying any option, verify the fix works:

### 1. Test TorchVision Fix
```bash
cd /workspace
python3 test_torchvision_circular_import_fix.py
```

**Expected Output:**
```
🔬 TorchVision Circular Import Fix Validation
============================================================
🧪 Testing TorchVision Circular Import Fix
==================================================
1️⃣ Applying TorchVision fix...
   ✅ TorchVision mock installed
...
🎉 COMPLETE SUCCESS: All tests passed!
   ✅ TorchVision circular import fix works
   ✅ FastAPI server can be imported
   🚀 Ready to start the web interface!
```

### 2. Test FastAPI Server Startup
```bash
python3 start_fastapi_with_fix.py
```

**Expected Output:**
```
🌐 TorchVision-Safe FastAPI Server Startup
==================================================
🔧 Applying comprehensive TorchVision circular import fix...
   📦 Creating comprehensive TorchVision mock...
   ✅ Comprehensive TorchVision mock installed successfully
🚀 Starting FastAPI server with TorchVision fix...
   📡 Starting uvicorn server on port 80...
INFO:     Started server process [PID]
INFO:     Uvicorn running on http://0.0.0.0:80
```

### 3. Test Web Interface
```bash
bash run_web_demo.sh
```

**Should start without errors and show:**
```
🌐 Starting HunyuanVideo-Avatar Web Interface...
==============================================
✅ Starting FastAPI backend server with TorchVision fix...
✅ FastAPI server started (PID: X)
✅ Starting Gradio web interface...
```

---

## 📋 What Files Were Added

The new TorchVision fix includes:

1. **`start_fastapi_with_fix.py`** - TorchVision-safe FastAPI startup script
2. **`test_torchvision_circular_import_fix.py`** - Validation test script  
3. **`TORCHVISION_CIRCULAR_IMPORT_FIX.md`** - Technical documentation
4. **`PROBLEM_ANALYSIS_AND_SOLUTION.md`** - Complete solution summary
5. **Updated `hymm_gradio/fastapi_server.py`** - Pre-import TorchVision fix
6. **Updated `run_web_demo.sh`** - Uses new safe startup script

---

## 🎯 Recommendation

**Start with Option 1 (Quick Fix)** for immediate resolution, then implement **Option 2 (Docker Rebuild)** for a permanent solution.

### Quick Command Sequence:
```bash
# SSH into your RunPod container
ssh root@<your-pod-ip>

# Pull latest code
cd /workspace
git fetch origin
git checkout wan2gp  
git pull origin wan2gp

# Test the fix
python3 test_torchvision_circular_import_fix.py

# Restart web interface
bash run_web_demo.sh
```

---

## 🔍 Troubleshooting

### If git commands fail:
```bash
# Reset git state and pull fresh
cd /workspace
git reset --hard HEAD
git clean -fd
git fetch origin wan2gp
git checkout wan2gp
```

### If files are still missing:
```bash
# Manually download the key file
wget https://raw.githubusercontent.com/thanveerdev/HunyuanVideo-Avatar-minimal/wan2gp/start_fastapi_with_fix.py
chmod +x start_fastapi_with_fix.py
```

### If Docker build fails:
```bash
# Clean Docker cache and rebuild
docker system prune -a
docker build --no-cache -t thanveerdev/hunyuan-video-avatar:wan2gp .
```

---

## 🎉 Expected Result

After successful update, your RunPod container will:

- ✅ Start FastAPI server without TorchVision circular import errors
- ✅ Load the web interface on port 7860
- ✅ Process avatar generation requests successfully
- ✅ Maintain all existing VRAM optimization features
- ✅ Provide stable, reliable service

The TorchVision circular import issue will be completely resolved! 