#!/usr/bin/env python3
"""
Network Volume Utilities for HunyuanVideo Avatar
Provides functions to manage persistent storage on RunPod network volumes
"""

import os
import shutil
import glob
from datetime import datetime
from pathlib import Path
import json

# Network volume paths
NETWORK_VOLUME_BASE = "/network_volume"
OUTPUTS_DIR = os.path.join(NETWORK_VOLUME_BASE, "outputs")
VIDEOS_DIR = os.path.join(OUTPUTS_DIR, "videos")
AUDIO_DIR = os.path.join(OUTPUTS_DIR, "audio")
TEMP_DIR = os.path.join(OUTPUTS_DIR, "temp")
LOGS_DIR = os.path.join(NETWORK_VOLUME_BASE, "logs")
CACHE_DIR = os.path.join(NETWORK_VOLUME_BASE, "cache")

def ensure_network_volume_structure():
    """Ensure all required directories exist in the network volume."""
    directories = [
        OUTPUTS_DIR,
        VIDEOS_DIR,
        AUDIO_DIR,
        TEMP_DIR,
        LOGS_DIR,
        CACHE_DIR
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Ensured directory exists: {directory}")

def get_network_volume_info():
    """Get information about network volume usage and capacity."""
    try:
        # Get disk usage
        total, used, free = shutil.disk_usage(NETWORK_VOLUME_BASE)
        
        # Count files
        video_count = len(glob.glob(os.path.join(VIDEOS_DIR, "*.mp4")))
        audio_count = len(glob.glob(os.path.join(AUDIO_DIR, "*.wav")))
        
        # Get directory sizes
        def get_dir_size(path):
            total = 0
            try:
                for dirpath, dirnames, filenames in os.walk(path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        total += os.path.getsize(fp)
            except FileNotFoundError:
                pass
            return total
        
        outputs_size = get_dir_size(OUTPUTS_DIR)
        cache_size = get_dir_size(CACHE_DIR)
        logs_size = get_dir_size(LOGS_DIR)
        
        info = {
            "disk_usage": {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "usage_percent": round((used / total) * 100, 1)
            },
            "file_counts": {
                "videos": video_count,
                "audio_files": audio_count
            },
            "directory_sizes": {
                "outputs_mb": round(outputs_size / (1024**2), 2),
                "cache_mb": round(cache_size / (1024**2), 2),
                "logs_mb": round(logs_size / (1024**2), 2)
            },
            "paths": {
                "base": NETWORK_VOLUME_BASE,
                "outputs": OUTPUTS_DIR,
                "videos": VIDEOS_DIR,
                "audio": AUDIO_DIR,
                "temp": TEMP_DIR,
                "logs": LOGS_DIR,
                "cache": CACHE_DIR
            }
        }
        
        return info
    
    except Exception as e:
        print(f"❌ Error getting network volume info: {e}")
        return None

def create_timestamped_output_folder(prefix="generation"):
    """Create a timestamped folder for a new generation."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{timestamp}_{prefix}"
    folder_path = os.path.join(OUTPUTS_DIR, folder_name)
    
    os.makedirs(folder_path, exist_ok=True)
    
    # Create subfolders
    os.makedirs(os.path.join(folder_path, "video"), exist_ok=True)
    os.makedirs(os.path.join(folder_path, "audio"), exist_ok=True)
    os.makedirs(os.path.join(folder_path, "input"), exist_ok=True)
    
    return folder_path

def save_generation_metadata(folder_path, metadata):
    """Save metadata about a generation to the output folder."""
    metadata_file = os.path.join(folder_path, "metadata.json")
    
    # Add timestamp and paths
    metadata.update({
        "timestamp": datetime.now().isoformat(),
        "folder_path": folder_path,
        "network_volume_base": NETWORK_VOLUME_BASE
    })
    
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Saved metadata to: {metadata_file}")

def cleanup_temp_files(older_than_hours=1):
    """Clean up temporary files older than specified hours."""
    import time
    
    current_time = time.time()
    cutoff_time = current_time - (older_than_hours * 3600)
    
    temp_files = glob.glob(os.path.join(TEMP_DIR, "*"))
    cleaned_count = 0
    
    for file_path in temp_files:
        try:
            if os.path.getmtime(file_path) < cutoff_time:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    cleaned_count += 1
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    cleaned_count += 1
        except Exception as e:
            print(f"⚠️  Could not clean {file_path}: {e}")
    
    print(f"🧹 Cleaned {cleaned_count} temporary files/folders")
    return cleaned_count

def get_recent_generations(limit=10):
    """Get list of recent generations with their metadata."""
    generations = []
    
    # Get all generation folders
    pattern = os.path.join(OUTPUTS_DIR, "*_generation")
    folders = glob.glob(pattern)
    
    # Sort by modification time (newest first)
    folders.sort(key=os.path.getmtime, reverse=True)
    
    for folder in folders[:limit]:
        metadata_file = os.path.join(folder, "metadata.json")
        
        generation_info = {
            "folder": os.path.basename(folder),
            "path": folder,
            "timestamp": datetime.fromtimestamp(os.path.getmtime(folder)).isoformat(),
            "size_mb": round(get_folder_size(folder) / (1024**2), 2)
        }
        
        # Add metadata if available
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    generation_info["metadata"] = metadata
            except Exception as e:
                print(f"⚠️  Could not read metadata for {folder}: {e}")
        
        generations.append(generation_info)
    
    return generations

def get_folder_size(folder_path):
    """Get the total size of a folder in bytes."""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
    except FileNotFoundError:
        pass
    return total

def export_generation(folder_name, export_path):
    """Export a generation folder to a specified path."""
    source_path = os.path.join(OUTPUTS_DIR, folder_name)
    
    if not os.path.exists(source_path):
        print(f"❌ Generation folder not found: {source_path}")
        return False
    
    try:
        shutil.copytree(source_path, export_path)
        print(f"✅ Exported generation to: {export_path}")
        return True
    except Exception as e:
        print(f"❌ Error exporting generation: {e}")
        return False

def print_network_volume_summary():
    """Print a summary of network volume status."""
    print("\n" + "="*60)
    print("🗂️  NETWORK VOLUME SUMMARY")
    print("="*60)
    
    info = get_network_volume_info()
    if not info:
        print("❌ Could not get network volume information")
        return
    
    # Disk usage
    disk = info["disk_usage"]
    print(f"💾 Disk Usage: {disk['used_gb']:.1f}GB / {disk['total_gb']:.1f}GB ({disk['usage_percent']:.1f}%)")
    print(f"📊 Free Space: {disk['free_gb']:.1f}GB")
    
    # File counts
    files = info["file_counts"]
    print(f"🎬 Generated Videos: {files['videos']}")
    print(f"🎵 Audio Files: {files['audio_files']}")
    
    # Directory sizes
    sizes = info["directory_sizes"]
    print(f"📁 Outputs: {sizes['outputs_mb']:.1f}MB")
    print(f"🗄️  Cache: {sizes['cache_mb']:.1f}MB")
    print(f"📝 Logs: {sizes['logs_mb']:.1f}MB")
    
    print("\n🗂️  Recent Generations:")
    recent = get_recent_generations(5)
    for gen in recent:
        print(f"  • {gen['folder']} ({gen['size_mb']:.1f}MB)")
    
    print("="*60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python network_volume_utils.py <command>")
        print("Commands:")
        print("  setup    - Ensure network volume structure")
        print("  info     - Show network volume information")
        print("  summary  - Show detailed summary")
        print("  cleanup  - Clean temporary files")
        print("  recent   - Show recent generations")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "setup":
        ensure_network_volume_structure()
    elif command == "info":
        info = get_network_volume_info()
        if info:
            print(json.dumps(info, indent=2))
    elif command == "summary":
        print_network_volume_summary()
    elif command == "cleanup":
        cleanup_temp_files()
    elif command == "recent":
        recent = get_recent_generations()
        for gen in recent:
            print(f"{gen['folder']} - {gen['timestamp']} ({gen['size_mb']:.1f}MB)")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1) 