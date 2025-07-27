import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import subprocess
import tempfile
import os
import requests
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
import time
from elevenlabs import client

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
elevenlabs_api_key = os.getenv("ELEVEN_LABS_API_KEY")

# Initialize ElevenLabs client
if elevenlabs_api_key:
    elevenlabs_client = client.ElevenLabs(api_key=elevenlabs_api_key)
else:
    elevenlabs_client = None

# Initialize Groq LLM
@st.cache_resource
def initialize_llm():
    llm = ChatGroq(model="llama3-8b-8192")
    question_prompt = PromptTemplate(
        input_variables=["question"],
        template="Shortly, answer this question: {question}.",
    )
    memory = ConversationBufferWindowMemory(k=5)
    question_chain = LLMChain(llm=llm, prompt=question_prompt, 
                              output_key="question", 
                              memory=memory)
    return question_chain

# Initialize the LLM chain
question_chain = initialize_llm()

def record_audio(duration=5, sample_rate=44100):
    """Record audio for specified duration"""
    st.info(f"Recording for {duration} seconds...")
    
    # Record audio
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    
    return audio, sample_rate

def save_audio_to_temp(audio, sample_rate):
    """Save audio to a temporary file"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        write(temp_file.name, sample_rate, audio)
        return temp_file.name

def transcribe_audio(audio_file):
    """Transcribe audio using Whisper"""
    try:
        result = subprocess.run(
            ["whisper", audio_file, "--model", "tiny", "--language", "English"], 
            capture_output=True, 
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return None

def get_llm_response(question):
    """Get response from Groq LLM"""
    try:
        answer = question_chain.invoke({"question": question})
        return answer.get("question", "No response generated")
    except Exception as e:
        st.error(f"Error getting LLM response: {e}")
        return None

def text_to_speech_elevenlabs(text, voice_id="21m00Tcm4TlvDq8ikWAM", output_file="response.wav"):
    """Convert text to speech using ElevenLabs API"""
    if not elevenlabs_client:
        st.error("ElevenLabs API key not found. Please add ELEVEN_LABS_API_KEY to your .env file")
        return None
    
    try:
        st.info("🎵 Generating speech from AI response...")
        
        # Generate audio using ElevenLabs
        audio = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_monolingual_v1"
        )
        
        # Save the audio file
        with open(output_file, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        st.success("✅ Speech generated successfully!")
        return output_file
            
    except Exception as e:
        st.error(f"Error in text-to-speech: {e}")
        return None

def play_audio_file(audio_file):
    """Play audio file in Streamlit"""
    try:
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        
        st.audio(audio_bytes, format="audio/wav")
        return True
    except Exception as e:
        st.error(f"Error playing audio: {e}")
        return False

# Streamlit UI
st.set_page_config(page_title="Voice Talk with Groq", page_icon="🎤", layout="wide")

st.title("🎤 Voice Talk with Groq LLM")
st.markdown("Record your voice, convert to text, and get AI responses!")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    recording_duration = st.slider("Recording Duration (seconds)", 3, 15, 5)
    sample_rate = st.selectbox("Sample Rate", [22050, 44100, 48000], index=1)
    
    st.markdown("---")
    st.header("Voice Settings")
    
    # ElevenLabs voice selection
    voice_options = {
        "Aria (Female)": "9BWtsMINqrJLrRacOk9x",
        "Sarah (Female)": "EXAVITQu4vr4xnSDxMaL",
        "Laura (Female)": "FGY2WhTYpPnrIDTdsKH5",
        "Charlie (Male)": "IKne3meq5aSn9XLyUdCD",
        "George (Male)": "JBFqnCBsd6RMkjVDRZzb"
    }
    
    selected_voice = st.selectbox(
        "AI Voice", 
        list(voice_options.keys()), 
        index=0,
        help="Select the voice for AI responses"
    )
    
    # Voice stability and similarity boost
    voice_stability = st.slider("Voice Stability", 0.0, 1.0, 0.5, 0.1, help="Higher values make voice more stable but less expressive")
    voice_similarity = st.slider("Voice Similarity", 0.0, 1.0, 0.75, 0.1, help="Higher values make voice more similar to original")
    
    # Voice speed control
    voice_speed = st.slider("Voice Speed", 0.5, 2.0, 1.0, 0.1, help="Adjust the speed of AI voice responses")
    
    st.markdown("---")
    st.markdown("### Instructions")
    st.markdown("1. Click 'Start Recording' to begin")
    st.markdown("2. Speak clearly into your microphone")
    st.markdown("3. Wait for transcription and AI response")
    st.markdown("4. Listen to the AI voice response")
    st.markdown("5. View conversation history below")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🎙️ Voice Recording")
    
    if st.button("🎤 Start Recording", type="primary", use_container_width=True):
        # Create a placeholder for recording status
        status_placeholder = st.empty()
        
        with status_placeholder.container():
            st.info("🎙️ Recording in progress... Please speak now!")
            
        # Record audio
        audio, sr = record_audio(recording_duration, sample_rate)
        
        # Save to temporary file
        temp_audio_file = save_audio_to_temp(audio, sr)
        
        # Update status
        status_placeholder.success("✅ Recording completed! Processing...")
        
        # Transcribe audio
        with st.spinner("Converting speech to text..."):
            transcribed_text = transcribe_audio(temp_audio_file)
        
        if transcribed_text:
            st.success("🎯 Transcription successful!")
            st.text_area("Transcribed Text:", transcribed_text, height=100)
            
            # Get LLM response
            with st.spinner("Getting AI response..."):
                llm_response = get_llm_response(transcribed_text)
            
            if llm_response:
                st.success("🤖 AI Response received!")
                st.text_area("AI Response:", llm_response, height=150)
                
                # Convert AI response to speech
                voice_id = voice_options[selected_voice]
                audio_file = text_to_speech_elevenlabs(llm_response, voice_id, "response.wav")
                
                if audio_file:
                    st.markdown("### 🎵 AI Voice Response")
                    play_audio_file(audio_file)
                
                # Store in session state for conversation history
                if 'conversation_history' not in st.session_state:
                    st.session_state.conversation_history = []
                
                st.session_state.conversation_history.append({
                    'user_question': transcribed_text,
                    'ai_response': llm_response,
                    'ai_voice_file': audio_file if audio_file else None,
                    'timestamp': time.strftime("%H:%M:%S")
                })
        
        # Clean up temporary file
        try:
            os.unlink(temp_audio_file)
        except:
            pass

with col2:
    st.header("💬 Conversation History")
    
    if 'conversation_history' in st.session_state and st.session_state.conversation_history:
        for i, conv in enumerate(reversed(st.session_state.conversation_history)):
            with st.expander(f"Conversation {len(st.session_state.conversation_history) - i} - {conv['timestamp']}"):
                st.markdown("**You:**")
                st.write(conv['user_question'])
                st.markdown("**AI:**")
                st.write(conv['ai_response'])
                
                # Add audio playback for AI response if available
                if conv.get('ai_voice_file') and os.path.exists(conv['ai_voice_file']):
                    st.markdown("**🎵 AI Voice:**")
                    play_audio_file(conv['ai_voice_file'])
    else:
        st.info("No conversations yet. Start recording to see your conversation history!")

# Footer
st.markdown("---")
st.markdown("### Technical Details")
st.markdown(f"- **Sample Rate:** {sample_rate} Hz")
st.markdown(f"- **Recording Duration:** {recording_duration} seconds")
st.markdown("- **Speech-to-Text:** OpenAI Whisper (tiny model)")
st.markdown("- **AI Model:** Groq Llama3-8b-8192")
st.markdown("- **Text-to-Speech:** ElevenLabs API")
st.markdown(f"- **Selected Voice:** {selected_voice}")

# Add some styling
st.markdown("""
<style>
.stButton > button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
    font-size: 18px;
    font-weight: bold;
}
.stButton > button:hover {
    background-color: #ff3333;
    color: white;
}
</style>
""", unsafe_allow_html=True) 