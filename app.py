import streamlit as st
import openai
import base64
from PIL import Image
import io



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
    st.title('AddaAI Chatbot')

    # Persistent API key input fixed at the top
    with st.container():
        api_key = st.text_input("Enter your OpenAI API Key:", type="password", key="api_key")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'summary' not in st.session_state:
        st.session_state['summary'] = ""

    # Display the conversation history
    with st.container():
        for question, answer in st.session_state['chat_history']:
            st.text_area("Question:", value=question, height=100, key=question + "_q")
            st.text_area("Answer:", value=answer, height=150, key=answer + "_a")

        user_input = st.text_input("Type your message here:", key="user_input")
        uploaded_file = st.file_uploader("Upload an image related to your doubt", type=['png', 'jpg', 'jpeg'], key="file_uploader")

        if st.button('Send'):
            image_b64 = ""
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                image_b64 = encode_image_to_base64(image)

            if api_key and (user_input or image_b64):
                response = get_response(api_key, user_input, st.session_state['summary'], image_b64)
                st.session_state['chat_history'].append((user_input, response))
                
                if len(st.session_state['chat_history']) % 5 == 0:
                    chat_text = "\n".join([f"User: {q}\nAssistant: {a}" for q, a in st.session_state['chat_history']])
                    new_summary = summarize_conversation(api_key, chat_text)
                    st.session_state['summary'] = summarize_conversation(api_key, f"{st.session_state['summary']}\n{new_summary}")
                    st.session_state['chat_history'] = []  # Reset the history after summarization

                st.experimental_rerun()  # Rerun the app to clear the input and refresh the chat history
            else:
                st.error("An API key and at least a message or image are required to send.")

if __name__ == '__main__':
    main()
