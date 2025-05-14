from fastapi import FastAPI, HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

app= FastAPI()

@app.get("/ask/{question}")
async def ask_psychologist(question: str):
    try:
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=openai_api_key)
        prompt=ChatPromptTemplate.from_messages([
            ("system","You are psihicologist.Your task is to help people for overcome  depression anxiety,overthinking,maladaptive daydreaming "
            "and other mental problems.be a friendly and empathetic person."),
            ("user",question),
        ])
        chain=prompt | llm
        response = chain.invoke({"input": question})
        return {"response": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

