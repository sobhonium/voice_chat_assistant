from dotenv import load_dotenv
import os

# 1st method: using .env file.
load_dotenv()
# Access them using os.getenv or os.environ
api_key = os.getenv("GROQ_API_KEY")

# 2nd method: using hard code
# api_key = "<put the api key here>"
# if not os.environ.get("GROQ_API_KEY"):
#     os.environ["GROQ_API_KEY"] = api_key #getpass.getpass("Enter API key for Groq: ")


from langchain_groq import ChatGroq

llm = ChatGroq(model="llama3-8b-8192")
# llm2 = ChatGroq(model="llama3-8b-8192")



from langchain.prompts import PromptTemplate
question_prompt = PromptTemplate(
    input_variables=["question"],
    template="Shortly, anwser this question: {question}.",
)





from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain




# when using 1, it means it does not actually use memory
memory = ConversationBufferWindowMemory(k=5)
question_chain = LLMChain(llm=llm, prompt=question_prompt, 
                          output_key="question", 
                          memory=memory)




import sounddevice as sd
from scipy.io.wavfile import write
from io import BytesIO

while True:
    print("Recording...")
    # Set parameters
    duration = 5  # seconds
    samplerate = 44100  # samples per second
    # Record audio
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished

    print("Ask Groq-AI a Q:")

    # Save to a BytesIO object (in-memory WAV file)
    wav_io = BytesIO()
    write(wav_io, samplerate, audio)

    # To save to a real file instead, uncomment below:
    outputfile = "output.wav"
    print(f'saving voice in {outputfile}')
    write(outputfile, samplerate, audio)

    # Reset pointer to beginning if needed
    wav_io.seek(0)

    
    import subprocess

    # Run a command and capture output
    question = subprocess.run(["whisper", "output.wav", "--model", "tiny", "--language", "English"], 
                            capture_output=True, 
                            text=True)
    print('Question:', question.stdout)
    answer = question_chain.invoke({"question": question.stdout})
    
    # # Print output
    # print("STDOUT:")
    # print(result.stdout)

    print('Answer: ', answer)
    print('='*15)
    
    
    