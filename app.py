import streamlit as st
import openai
import wave
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

def whisper_transcribe(api_key, audio_file_path):
    openai.api_key = api_key
    try:
        with open(audio_file_path, 'rb') as audio_file:
            transcription = openai.Audio.transcribe("whisper-1", audio_file)
        return transcription['text']
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return None

def save_audio_file(audio_data, filename="recorded_audio.wav"):
    try:
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data)
        return filename
    except Exception as e:
        st.error(f"Error saving audio file: {str(e)}")
        return None

def main():
    st.title('Audio Recorder and Transcriber')

    api_key = st.text_input("Enter your OpenAI API Key:", type="password", key="api_key")

    if not api_key:
        st.warning("Please enter your OpenAI API key.")
        return

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
            if audio_file_path:
                # Transcribe the saved audio file
                transcription = whisper_transcribe(api_key, audio_file_path)
                if transcription:
                    st.subheader("Transcribed Audio")
                    st.write(transcription)

if __name__ == '__main__':
    main() 
