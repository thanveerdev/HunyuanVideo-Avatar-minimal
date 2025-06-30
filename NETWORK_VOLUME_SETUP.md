# 🗂️ Network Volume Setup Guide for HunyuanVideo Avatar

This guide explains how to set up and use a 10GB "videostore" network volume with your HunyuanVideo Avatar RunPod deployment for persistent storage.

## 📋 Prerequisites

- RunPod account with credits
- Access to create network volumes
- Basic familiarity with RunPod interface

## 🚀 Step 1: Create Network Volume

### 1.1 In RunPod Console:
1. Go to **Storage** → **Network Volumes**
2. Click **+ Create Network Volume**
3. Configure:
   - **Name**: `videostore`
   - **Size**: `10 GB`
   - **Data Center**: Choose same as your preferred pod location (e.g., `US-OR`, `US-CA`)
4. Click **Create Network Volume**
5. **Copy the Network Volume ID** (you'll need this)

### 1.2 Network Volume Name:
- **Primary**: `videostore` ✅ (Clean and simple)
- **Alternative**: `hunyuan-avatar-outputs` or `avatar-video-storage`

## 🔧 Step 2: Update RunPod Template

### 2.1 Modify `runpod_template.json`:
```json
{
  "networkVolumeId": "YOUR_NETWORK_VOLUME_ID_HERE",
  "networkVolumeMountPath": "/network_volume"
}
```

Replace `YOUR_NETWORK_VOLUME_ID_HERE` with the actual ID from Step 1.1.

### 2.2 Deploy with Network Volume:
1. Use the updated template when creating your pod
2. Or manually add network volume in pod creation:
   - **Network Volume**: Select your created volume
   - **Mount Path**: `/network_volume`

## 📁 Step 3: Directory Structure

Once your pod starts, the network volume will have this structure:

```
/network_volume/
├── outputs/                 # Main outputs directory
│   ├── videos/             # Generated videos (.mp4)
│   ├── audio/              # Processed audio files (.wav)
│   ├── temp/               # Temporary files (auto-cleaned)
│   └── README.txt          # Welcome message with info
├── logs/                   # Application logs
│   └── startup.log         # Pod startup information
└── cache/                  # Model cache (optional)
```

## 🎯 Step 4: Using the Network Volume

### 4.1 Automatic Setup:
- The `docker_startup_network_volume.sh` script automatically:
  - Creates all required directories
  - Sets proper permissions
  - Creates symbolic links for compatibility
  - Logs startup information

### 4.2 Environment Variables:
These are automatically set when using the network volume startup script:
- `OUTPUT_BASE=/network_volume/outputs`
- `PERSISTENT_STORAGE=/network_volume`
- `CACHE_DIR=/network_volume/cache`
- `LOG_DIR=/network_volume/logs`

## 🛠️ Step 5: Management Commands

### 5.1 Network Volume Utilities:
```bash
# Check network volume status
python network_volume_utils.py summary

# Get detailed information
python network_volume_utils.py info

# Clean temporary files
python network_volume_utils.py cleanup

# List recent generations
python network_volume_utils.py recent
```

### 5.2 Manual Management:
```bash
# Check disk usage
df -h /network_volume

# List outputs
ls -la /network_volume/outputs/

# View startup logs
tail -f /network_volume/logs/startup.log
```

## 📊 Step 6: Storage Capacity Planning

### 6.1 Typical File Sizes:
- **High Quality (1024px, 2min)**: ~200-500MB per video
- **Balanced (512px, 1min)**: ~50-150MB per video
- **Low Quality (256px, 30s)**: ~10-30MB per video

### 6.2 10GB Capacity Estimates:
- **High Quality**: 20-50 videos
- **Balanced**: 65-200 videos
- **Low Quality**: 330-1000 videos

### 6.3 Storage Optimization:
- Temporary files are auto-cleaned after 1 hour
- Use `python network_volume_utils.py cleanup` for manual cleanup
- Export/download videos you want to keep long-term
- Delete old generations when storage is full

## 🔄 Step 7: Pod Lifecycle Management

### 7.1 Pod Restart:
✅ **Persistent**: All outputs saved to network volume remain
✅ **Automatic**: Network volume remounts automatically
✅ **Logs**: Startup logs accumulate with timestamps

### 7.2 Pod Recreation:
✅ **Persistent**: Your videos and data are preserved
✅ **Configuration**: Use same network volume ID in new pod
✅ **History**: All generation history is maintained

### 7.3 Pod Termination:
✅ **Safe**: Network volume data is completely independent
✅ **Billing**: Only pay for pod usage, network volume bills separately
✅ **Access**: Can mount same volume to new pods anytime

## 🚨 Step 8: Troubleshooting

### 8.1 Network Volume Not Mounting:
```bash
# Check if network volume is mounted
ls -la /network_volume

# Check mount status
mount | grep network_volume

# Manual mount (if needed)
sudo mount -t nfs4 NETWORK_VOLUME_IP:/volumes/VOLUME_ID /network_volume
```

### 8.2 Permission Issues:
```bash
# Fix permissions
sudo chmod -R 755 /network_volume
sudo chown -R $USER:$USER /network_volume
```

### 8.3 Storage Full:
```bash
# Check usage
python network_volume_utils.py summary

# Clean temporary files
python network_volume_utils.py cleanup

# List largest files
du -h /network_volume/outputs/* | sort -rh | head -10
```

### 8.4 Application Not Using Network Volume:
```bash
# Check environment variables
env | grep OUTPUT

# Verify symbolic links
ls -la /workspace/outputs

# Check configuration
cat config_minimal.py | grep save_path
```

## 💡 Step 9: Best Practices

### 9.1 Regular Maintenance:
- Check storage usage weekly: `python network_volume_utils.py summary`
- Clean temporary files: `python network_volume_utils.py cleanup`
- Export important videos to local storage
- Monitor startup logs for issues

### 9.2 Backup Strategy:
- Download important generations locally
- Use RunPod's snapshot feature (if available)
- Export generations: `python network_volume_utils.py export <folder> <path>`

### 9.3 Cost Optimization:
- Network volumes have ongoing costs (~$0.20/GB/month)
- Delete old files when storage is full
- Consider larger volumes if frequently generating videos
- Use temporary pod storage for intermediate files

## 📈 Step 10: Scaling Up

### 10.1 Increasing Volume Size:
1. Go to RunPod **Storage** → **Network Volumes**
2. Find your volume and click **Resize**
3. Increase size (can only increase, not decrease)
4. Restart pod to recognize new size

### 10.2 Multiple Volumes:
- Create separate volumes for different projects
- Use volume naming: `videostore-project1`, `videostore-project2`
- Mount multiple volumes: `/network_volume1`, `/network_volume2`

### 10.3 Shared Access:
- Same network volume can be mounted to multiple pods
- Useful for team projects or load distribution
- **Caution**: Ensure only one pod writes at a time

---

## ✅ Quick Setup Checklist

- [ ] Create 10GB network volume named `videostore`
- [ ] Copy network volume ID
- [ ] Update `runpod_template.json` with volume ID
- [ ] Deploy pod with network volume mounted at `/network_volume`
- [ ] Verify startup script creates directory structure
- [ ] Test generation saves to `/network_volume/outputs`
- [ ] Run `python network_volume_utils.py summary` to verify setup

---

## 🆘 Need Help?

### Common Issues:
1. **Volume not mounting**: Check volume ID and mount path
2. **Permission denied**: Run permission fix commands
3. **Storage full**: Clean temporary files and old generations
4. **App not saving to volume**: Check environment variables and config

### Useful Commands:
```bash
# Complete status check
python network_volume_utils.py summary

# View configuration
echo $OUTPUT_BASE
cat config_minimal.py | grep -A 5 -B 5 save_path

# Test write access
touch /network_volume/test_file && rm /network_volume/test_file && echo "✅ Write access OK"
```

**Happy generating with persistent storage! 🎬✨** 