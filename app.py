import json
import requests
import os
from openai import OpenAI
import streamlit as st
import openai


MODEL ="gpt-3.5-turbo-0125"
MODEL_function_call= "gpt-3.5-turbo-0125"


client = OpenAI(
  api_key="sk-proj-vsHEz8Asni5Iaqx4ToyST3BlbkFJqAC8S4lnE1Uu6xkFG7iq",
)



def get_response(message):

 
    
    MODEL ="gpt-3.5-turbo-0125"


    Sys_Prompt= """

    <System_Prompt>
        <role>
            Your primary goal is to:

            2. Act as a helpful doubt solver and resolve student queries properly.

        </role>

       
    </System_Prompt>
    """
    
    try:
        
        response = client.chat.completions.create(
            model=MODEL,


            messages = [
                       {"role": "system", "content": Sys_Prompt},
                       {"role": "user", "content": f"""

                        Here is the student's question:

                        {message}

                        """

                        },

                        {"role": "assistant", "content": " "}
                       ],

        )



        data = response.choices[0].message.content
        data = json.loads(data)


        return data



    except Exception as e:
        return f"An error occurred: {str(e)}"







def main():
    st.title('AddaAI Chatbot')
    
    user_input = st.text_input("Type your message here:")
    
    if st.button('Send'):
        if user_input:
            response = get_response(user_input)
            st.text_area("AddaAI Response:", value=response, height=200)
        else:
            st.write("Please type a message to get a response.")

if __name__ == '__main__':
    main()
