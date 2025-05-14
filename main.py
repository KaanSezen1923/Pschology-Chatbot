from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=openai_api_key)

prompt=ChatPromptTemplate.from_messages([
    ("system","You are psihicologist.Your task is to help people for overcome  depression anxiety,overthinking,maladaptive daydreaming "
    "and other mental problems.be a friendly and empathetic person."),
    ("user","{input}"),
     
])

chain=prompt | llm
def main():
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = chain.invoke({"input": user_input})
        print("Psychologist:", response.content)
        
if __name__ == "__main__":
    main()