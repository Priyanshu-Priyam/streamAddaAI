import streamlit as st
import openai
import base64

def get_image_base64(image):
    """Converts an image to base64 string."""
    return base64.b64encode(image.read()).decode()

def handle_image_query(api_key, image_base64, prompt):
    """Send the base64 image and a prompt to the OpenAI API."""
    client = openai.OpenAI(api_key=api_key)
    full_prompt = f"{prompt}\n\nImage (base64): {image_base64}"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": "solve this user query"},
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

def main():
    st.title('AddaAI Chatbot')
    
    with st.container():
        api_key = st.text_input("Enter your OpenAI API Key:", type="password", key="api_key")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'summary' not in st.session_state:
        st.session_state['summary'] = ""

    with st.container():
        user_input = st.text_input("Type your message here:", key="user_input")
        uploaded_image = st.file_uploader("Or upload an image for analysis", type=["png", "jpg", "jpeg"])
        
        if user_input and not uploaded_image:
            if st.button('Send Text'):
                response = get_response(api_key, user_input, st.session_state['summary'])
                st.session_state['chat_history'].append((user_input, response))

        if uploaded_image and not user_input:
            if st.button('Send Image'):
                image_base64 = get_image_base64(uploaded_image)
                image_response = handle_image_query(api_key, image_base64, "solve this user query")
                st.session_state['chat_history'].append(("Uploaded Image", image_response))

        for question, answer in st.session_state['chat_history']:
            if question == "Uploaded Image":
                st.image(uploaded_image, caption="Uploaded Image")
            else:
                st.text_area("Question:", value=question, height=100, key=question + "_q")
            st.text_area("Answer:", value=answer, height=150, key=answer + "_a")

        if len(st.session_state['chat_history']) % 5 == 0 and st.session_state['chat_history']:
            chat_text = "\n".join([f"User: {q}\nAssistant: {a}" for q, a in st.session_state['chat_history']])
            new_summary = summarize_conversation(api_key, chat_text)
            st.session_state['summary'] = summarize_conversation(api_key, f"{st.session_state['summary']}\n{new_summary}")
            st.session_state['chat_history'] = []

    if st.session_state['chat_history']:
        st.experimental_rerun()

if __name__ == '__main__':
    main()
