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

    # Persistent API key input fixed at the top
    with st.container():
        api_key = st.text_input("Enter your OpenAI API Key:", type="password", key="api_key")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Display the conversation history
    with st.container():
        for question, answer in st.session_state['chat_history']:
            st.text_area("Question:", value=question, height=100, key=question + "_q")
            st.text_area("Answer:", value=answer, height=150, key=answer + "_a")

        user_input = st.text_input("Type your message here:", key="user_input")

        if st.button('Send'):
            if user_input and api_key:
                response = get_response(api_key, user_input)
                st.session_state['chat_history'].append(("You: " + user_input, "AddaAI: " + response))
                st.experimental_rerun()  # Rerun the app to clear the input and refresh the chat history
            else:
                st.error("Both API key and a message are required to send.")

if __name__ == '__main__':
    main()
