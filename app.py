import json
import streamlit as st
import openai

def get_response(api_key, message):
    client = openai.OpenAI(api_key=api_key)

    system_prompt = """
    <System_Prompt>
        <role>
            Your primary goal is to:
            2. Act as a helpful doubt solver and resolve student queries properly.
        </role>
    </System_Prompt>
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the student's question:\n\n{message}"},
                {"role": "assistant", "content": " "}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    st.title('AddaAI Chatbot')

    # Input for API Key
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    user_input = st.text_input("Type your message here:", key="user_input")

    if st.button('Send') and api_key and user_input:
        response = get_response(api_key, user_input)
        # Store the pair of question and response in session state
        st.session_state['chat_history'].append(("You: " + user_input, "AddaAI: " + response))
        # Clear input box after sending
        st.session_state.user_input = ""

    # Display the conversation history
    for question, answer in st.session_state['chat_history']:
        st.text_area("", value=question, height=100, key=question)
        st.text_area("", value=answer, height=150, key=answer)

    if not api_key:
        st.error("API Key is required to interact with OpenAI.")
    elif not user_input:
        st.error("Please type a message to get a response.")

if __name__ == '__main__':
    main()
