from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

class CodeRequest(BaseModel):
    description: str
    language: str

class Api8:
    def __init__(self, _client, router):
        self.client = _client
        router.add_api_route(
            path="/generate-project-structure", 
            endpoint=self.generate_code, 
            methods=["POST"]
        )
    
    def generateProjectStructureFromNL(self, description: str, language: str) -> str:
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that provides code to recommend a project directory structure as a dictionary in the specified language."},
                {"role": "user", "content": f"In {language} generate the project structure given the following description: {description}"}
            ],
            temperature=0,
            max_tokens=512,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        code_block = response.choices[0].message.content.strip()
        
        if not code_block:
            raise ValueError("No code was generated by the model.")
        
        return code_block

    async def generate_code(self, request: CodeRequest):
        if not request.description.strip():
            raise HTTPException(status_code=400, detail="Description cannot be empty.")
        if not request.language.strip():
            raise HTTPException(status_code=400, detail="Language cannot be empty.")
        
        try:
            code = await asyncio.to_thread(self.generateProjectStructureFromNL, request.description, request.language)
            return {"code": code}
        except ValueError as ve:
            raise HTTPException(status_code=500, detail=str(ve))
        except Exception:
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
