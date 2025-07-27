#!/usr/bin/env python3
"""
Setup script for Voice Talk with Groq LLM
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_whisper():
    """Check if Whisper is installed"""
    try:
        result = subprocess.run(["whisper", "--help"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def main():
    print("🎤 Setting up Voice Talk with Groq LLM")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check your pip installation.")
        sys.exit(1)
    
    # Install Whisper if not already installed
    if not check_whisper():
        print("🔄 Installing OpenAI Whisper...")
        if not run_command("pip install openai-whisper", "Installing OpenAI Whisper"):
            print("❌ Failed to install Whisper. Please install it manually:")
            print("   pip install openai-whisper")
            sys.exit(1)
    else:
        print("✅ OpenAI Whisper is already installed")
    
    # Check for .env file
    if not os.path.exists(".env"):
        print("⚠️  .env file not found!")
        print("📝 Please create a .env file with your API keys:")
        print("   GROQ_API_KEY=your_groq_api_key_here")
        print("   ELEVEN_LABS_API_KEY=your_elevenlabs_api_key_here")
        print("\nTo get the API keys:")
        print("\nGroq API Key:")
        print("1. Visit https://console.groq.com/")
        print("2. Sign up or log in")
        print("3. Create a new API key")
        print("4. Add it to your .env file")
        print("\nElevenLabs API Key:")
        print("1. Visit https://elevenlabs.io/")
        print("2. Sign up or log in")
        print("3. Go to Profile Settings → API Key")
        print("4. Copy your API key")
        print("5. Add it to your .env file")
    else:
        print("✅ .env file found")
        
        # Check if both API keys are present
        with open(".env", "r") as f:
            env_content = f.read()
        
        if "GROQ_API_KEY" not in env_content:
            print("⚠️  GROQ_API_KEY not found in .env file")
        else:
            print("✅ GROQ_API_KEY found")
            
        if "ELEVEN_LABS_API_KEY" not in env_content:
            print("⚠️  ELEVEN_LABS_API_KEY not found in .env file")
        else:
            print("✅ ELEVEN_LABS_API_KEY found")
    
    print("\n🎉 Setup completed!")
    print("\nTo run the application:")
    print("   streamlit run app.py")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 