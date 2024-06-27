import streamlit as st
import openai

# Set your OpenAI API key here
openai.api_key = 'your-openai-api-key'

def get_response(message):
    response = openai.Completion.create(
        engine="text-davinci-002", 
        prompt=message, 
        max_tokens=150
    )
    return response.choices[0].text.strip()

def main():
    st.title('OpenAI GPT Chatbot')
    
    user_input = st.text_input("Type your message here:")
    
    if st.button('Send'):
        if user_input:
            response = get_response(user_input)
            st.text_area("GPT-3 Response:", value=response, height=200)
        else:
            st.write("Please type a message to get a response.")

if __name__ == '__main__':
    main()
