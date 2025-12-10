"""Model download and setup script with dependency verification."""
import sys
from pathlib import Path
import subprocess


def check_dependencies():
    """Verify all required dependencies are installed.
    
    Returns:
        True if all dependencies available, False otherwise
    """
    print("🔍 Checking Python dependencies...")
    
    required_modules = [
        "torch",
        "transformers",
        "huggingface_hub",
        "faster_whisper",
        "soundfile",
        "httpx",
        "memori",
    ]
    
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            missing.append(module)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All Python dependencies OK. Proceeding with model setup...\n")
    return True


def check_ollama():
    """Check if Ollama is installed and accessible.
    
    Returns:
        True if Ollama found, False otherwise
    """
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ Ollama detected: {result.stdout.strip()}")
            print("   Make sure you've run: ollama pull llama3.1")
            return True
        else:
            print("❌ Ollama command failed")
            return False
    
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        print("   Install from: https://ollama.com")
        print("   Then run: ollama pull llama3.1")
        return False
    
    except Exception as e:
        print(f"⚠️  Could not check Ollama: {e}")
        return False


def setup_directories(base_dir: Path):
    """Create required directories.
    
    Args:
        base_dir: Base directory for all data
    """
    print("📁 Setting up directories...")
    
    directories = [
        base_dir / "models" / "llm",
        base_dir / "models" / "whisper",
        base_dir / "models" / "tts",
        base_dir / "uploads",
        base_dir / "audio",
        base_dir / "logs",
        base_dir / "memori",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")
    
    print()


def download_sarvam(model_dir: Path):
    """Download Sarvam-1 model.
    
    Args:
        model_dir: Directory to save model
    
    Returns:
        True if successful or already present
    """
    print("📥 Sarvam-1 (Indic LLM)...")
    
    if model_dir.exists() and any(model_dir.iterdir()):
        print("  ✅ Already present. Skipping download.")
        return True
    
    try:
        from huggingface_hub import snapshot_download
        
        print(f"  Downloading to {model_dir}...")
        snapshot_download(
            repo_id="sarvamai/sarvam-1",
            local_dir=str(model_dir),
            local_dir_use_symlinks=False
        )
        print("  ✅ Download complete")
        return True
    
    except Exception as e:
        print(f"  ❌ Download failed: {e}")
        return False


def download_whisper(model_dir: Path):
    """Download Whisper model.
    
    Args:
        model_dir: Directory to save model
    
    Returns:
        True if successful
    """
    print("📥 Whisper 'small' (STT)...")
    
    try:
        from faster_whisper import WhisperModel
        
        # This will download if not cached
        model = WhisperModel(
            "small",
            download_root=str(model_dir),
            device="cpu"
        )
        print("  ✅ Model ready")
        return True
    
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return False


def download_indic_parler_tts(model_dir: Path):
    """Download Indic-Parler TTS model.
    
    Args:
        model_dir: Directory to save model
    
    Returns:
        True if successful or already present
    """
    print("📥 Indic-Parler-TTS base...")
    
    if model_dir.exists() and any(model_dir.iterdir()):
        print("  ✅ Already present. Skipping download.")
        return True
    
    try:
        from huggingface_hub import snapshot_download
        
        print(f"  Downloading to {model_dir}...")
        snapshot_download(
            repo_id="ai4bharat/indic-parler-tts",
            local_dir=str(model_dir),
            local_dir_use_symlinks=False,
            token=None  # Set HF token if needed
        )
        print("  ✅ Download complete")
        return True
    
    except Exception as e:
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str or "gated" in error_str:
            print("  ❌ Access denied for Indic-Parler-TTS")
            print("     This model requires authentication.")
            print("     Run: huggingface-cli login")
            print("     Or accept the license on Hugging Face")
        else:
            print(f"  ❌ Download failed: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("  Drishti AI - Model Setup Script")
    print("=" * 60)
    print()
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Setup paths - use project's backend/models directory
    # Changed from Path.home() / "ai-data" to keep models in project
    script_dir = Path(__file__).parent  # scripts directory
    backend_dir = script_dir.parent      # backend directory
    base_dir = backend_dir / "models"    # models directory
    print(f"Base directory: {base_dir}\n")
    
    # Create directories
    setup_directories(base_dir)
    
    # Track results
    results = {
        "Ollama (llama3.1)": "SKIPPED",
        "Sarvam-1": "ERROR",
        "Whisper small": "ERROR",
        "Indic-Parler-TTS": "ERROR",
    }
    
    # Check Ollama
    ollama_ok = check_ollama()
    results["Ollama (llama3.1)"] = "DETECTED" if ollama_ok else "MISSING"
    print()
    
    # Download models
    sarvam_dir = base_dir / "models" / "llm" / "sarvam-1"
    if download_sarvam(sarvam_dir):
        results["Sarvam-1"] = "OK"
    print()
    
    whisper_dir = base_dir / "models" / "whisper"
    if download_whisper(whisper_dir):
        results["Whisper small"] = "OK"
    print()
    
    tts_dir = base_dir / "models" / "tts" / "indic-parler"
    if download_indic_parler_tts(tts_dir):
        results["Indic-Parler-TTS"] = "OK"
    print()
    
    # Print summary
    print("=" * 60)
    print("  MODEL SETUP SUMMARY")
    print("=" * 60)
    for model, status in results.items():
        print(f"{model:25} : {status}")
    print("-" * 60)
    print()
    print("✨ Drishti AI model setup script finished.")
    print()


if __name__ == "__main__":
    main()
