import streamlit as st
import openai

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

        if st.button('Send'):
            if user_input and api_key:
                response = get_response(api_key, user_input, st.session_state['summary'])
                st.session_state['chat_history'].append((user_input, response))
                
                if len(st.session_state['chat_history']) % 5 == 0:
                    # Summarize the latest conversations or all conversations if this is the first summary
                    chat_text = "\n".join([f"User: {q}\nAssistant: {a}" for q, a in st.session_state['chat_history']])
                    new_summary = summarize_conversation(api_key, chat_text)
                    st.session_state['summary'] = summarize_conversation(api_key, f"{st.session_state['summary']}\n{new_summary}")
                    st.session_state['chat_history'] = []  # Reset the history after summarization

                st.experimental_rerun()  # Rerun the app to clear the input and refresh the chat history
            else:
                st.error("Both API key and a message are required to send.")

if __name__ == '__main__':
    main()
