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

    user_input = st.text_input("Type your message here:")
    
    if st.button('Send'):
        if user_input and api_key:
            response = get_response(api_key, user_input)
            st.text_area("AddaAI Response:", value=response, height=200)
        elif not api_key:
            st.error("API Key is required to interact with OpenAI.")
        else:
            st.error("Please type a message to get a response.")

if __name__ == '__main__':
    main()
