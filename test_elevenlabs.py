#!/usr/bin/env python3
"""
Test script for ElevenLabs API integration
"""

import os
from dotenv import load_dotenv
from elevenlabs import client

def test_elevenlabs_api():
    """Test ElevenLabs API connection"""
    load_dotenv()
    
    api_key = os.getenv("ELEVEN_LABS_API_KEY")
    
    if not api_key:
        print("❌ ELEVEN_LABS_API_KEY not found in .env file")
        return False
    
    print("🔄 Testing ElevenLabs API connection...")
    
    try:
        # Initialize ElevenLabs client
        elevenlabs_client = client.ElevenLabs(api_key=api_key)
        
        # Test with a simple text
        test_text = "Hello, this is a test of the ElevenLabs text-to-speech API."
        
        # Generate audio using ElevenLabs
        audio = elevenlabs_client.text_to_speech.convert(
            text=test_text,
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
            model_id="eleven_monolingual_v1"
        )
        
        # Save test audio
        with open("test_response.wav", "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        print("✅ ElevenLabs API test successful!")
        print("✅ Test audio saved as 'test_response.wav'")
        
        # List available voices
        print("\n📋 Available voices:")
        all_voices = elevenlabs_client.voices.get_all()
        for voice in all_voices.voices[:5]:  # Show first 5 voices
            print(f"  - {voice.name} (ID: {voice.voice_id})")
        
        return True
            
    except Exception as e:
        print(f"❌ Error testing ElevenLabs API: {e}")
        return False

if __name__ == "__main__":
    test_elevenlabs_api() 