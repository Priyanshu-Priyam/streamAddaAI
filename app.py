import streamlit as st
import openai
import base64
from PIL import Image
import io

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
            model="gpt-3.5-turbo-0125",  # Ensure consistency in model usage
            messages=[
                {"role": "system", "content": prompt},
                {"role": "assistant", "content": " "}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def get_response(api_key, message, context):
    client = openai.OpenAI(api_key=api_key)
    full_prompt = f"This is the summary of previous responses:\n{context}\n\nThis is the current question and answer pair:\nUser: {message}\nAssistant:"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": message},
                {"role": "assistant", "content": " "}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def process_image_and_query(api_key, base64_image, query_prompt, context):
    client = openai.OpenAI(api_key=api_key)
    full_prompt = f"This is the summary of previous responses:\n{context}\n\n{query_prompt}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "image", "content": base64_image},
                {"role": "assistant", "content": " "}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

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

        # Image upload functionality
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

            user_input = st.text_input("Type your message here (optional):", key="user_input")
            
            if st.button('Send'):
                if api_key:
                    if user_input:
                        response = get_response(api_key, user_input, st.session_state['summary'])
                        st.session_state['chat_history'].append((user_input, response))
                    # Process image and query
                    query_prompt = "solve this user query"
                    image_response = process_image_and_query(api_key, base64_image, query_prompt, st.session_state['summary'])
                    st.session_state['chat_history'].append(("Image Query:", image_response))

                    # Update summary after every interaction
                    chat_text = "\n".join([f"User: {q}\nAssistant: {a}" for q, a in st.session_state['chat_history']])
                    new_summary = summarize_conversation(api_key, chat_text)
                    st.session_state['summary'] = summarize_conversation(api_key, f"{st.session_state['summary']}\n{new_summary}")
                    st.experimental_rerun()  # Rerun the app to clear the input and refresh the chat history
                else:
                    st.error("API key is required to send.")

if __name__ == '__main__':
    main()
