import streamlit as st
import openai
import base64
from PIL import Image
import io
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

def whisper_transcribe(audio_file_path):
    with open(audio_file_path, 'rb') as audio_file:
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
    return transcription['text']

def save_audio_file(audio_data, filename="recorded_audio.wav"):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_data)
    return filename



MODEL ="gpt-4o"

def summarize_conversation(api_key, text):
    client = openai.OpenAI(api_key=api_key)
    system_prompt = """
    Summarize the following text, preserving key information. This summary should include
    the essence of the user questions and assistant answers to provide a clear context for any
    future interactions.
    """
    
    prompt = f"{system_prompt}\n\n{text}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "assistant", "content": " "}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def get_response(api_key, message, context, image_b64=None):
    client = openai.OpenAI(api_key=api_key)
    if message and image_b64:
        
        base64_image = image_b64
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": f"You are a helpful assistant that responds in Markdown, help the user with his/her query.  Here is the summary of previous conversation with this user : {context}"},
                {"role": "user", "content": [
                    {"type": "text", "text": message},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"}
                    }
                ]}
            ],
            temperature=0.0,
        )
        
        return response.choices[0].message.content
        
    elif image_b64:
                
        base64_image = image_b64
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": f"You are a helpful assistant that responds in Markdown, help the user with his/her query. Here is the summary of previous conversation with this user : {context} "},
                {"role": "user", "content": [
                    {"type": "text", "text": "Solve it"},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"}
                    }
                ]}
            ],
            temperature=0.0,
        )
        
        return response.choices[0].message.content
        
    else:
        full_prompt = f"This is the summary of previous responses:\n{context}\n\nThis is the current question and answer pair:\nUser: {message}\nAssistant:"    
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": message},
                {"role": "assistant", "content": " "}
            ],
        )
        return response.choices[0].message.content


def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")  # You can change "JPEG" to "PNG" if you prefer
    return base64.b64encode(buffered.getvalue()).decode('utf-8')



def main():
    st.title('AddaAI Chatbot with Audio Support')

    with st.container():
        api_key = st.text_input("Enter your OpenAI API Key:", type="password", key="api_key")

    rtc_configuration = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    webrtc_ctx = webrtc_streamer(
        key="audio-recorder",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_configuration,
        media_stream_constraints={"audio": True, "video": False},
        audio_receiver_size=1024,
    )

    if webrtc_ctx.audio_receiver:
        audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=None)
        audio_data = b''.join([frame.to_ndarray().tobytes() for frame in audio_frames])

        if st.button("Transcribe Audio"):
            # Save audio data to a WAV file
            audio_file_path = save_audio_file(audio_data)
            # Transcribe the saved audio file
            transcription = whisper_transcribe(audio_file_path)
            st.write(transcription)

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'summary' not in st.session_state:
        st.session_state['summary'] = ""
    if 'uploaded_image' not in st.session_state:
        st.session_state['uploaded_image'] = None

    with st.container():
        for question, answer, img in st.session_state['chat_history']:
            st.text_area("Question:", value=question, height=100, key=question + "_q")
            st.text_area("Answer:", value=answer, height=150, key=answer + "_a")
            if img is not None:
                st.image(img, caption="Uploaded Image", use_column_width=True)

        user_input = st.text_input("Type your message here:", key="user_input")
        uploaded_file = st.file_uploader("Upload an image related to your doubt", type=['png', 'jpg', 'jpeg'], key="file_uploader")

        if st.button('Send'):
            image_b64 = ""
            display_image = None
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                image_b64 = encode_image_to_base64(image)
                display_image = image  # We'll use this to display in the app

            if api_key and (user_input or image_b64):
                response = get_response(api_key, user_input, st.session_state['summary'], image_b64)
                st.session_state['chat_history'].append((user_input, response, display_image))
                
                if len(st.session_state['chat_history']) % 5 == 0:
                    chat_text = "\n".join([f"User: {q}\nAssistant: {a}" for q, a, _ in st.session_state['chat_history']])
                    new_summary = summarize_conversation(api_key, chat_text)
                    st.session_state['summary'] = summarize_conversation(api_key, f"{st.session_state['summary']}\n{new_summary}")
                    st.session_state['chat_history'] = []  # Reset the history after summarization

                st.experimental_rerun()  # Rerun the app to clear the input and refresh the chat history
            else:
                st.error("An API key and at least a message or image are required to send.")
                
if _name_ == '_main_':
    main()
