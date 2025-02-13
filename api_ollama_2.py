from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import requests
import ollama
import json
from pydantic import BaseModel

BASE_URL = "/ollama_api/poc"

app = FastAPI(title="poc testing",
              docs_url=BASE_URL+"/apidocs",
              redoc_url=BASE_URL+"/redoc")

def call_restaurants_api(cuisine: str, dish: str, budget: str):
    """Call the restaurants API."""
    url = "http://127.0.0.1:8002/restaurants/search"
    payload = {"cuisine":cuisine,"dish":dish,"budget":budget}  # Use passed arguments
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        return response.json()  # Return JSON
    else:
        return f"API request failed with status code: {response.status_code}"

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict]] = []

# model = "llama3.2_food_agent_v0.1"
# model = "llama3.2:1b_Agent_4_iter4"
model = "marco-v2-llama3.2:3b"

@app.post("/chat")
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    try:
        # messages = chat_request.conversation_history + [{'role': 'user', 'content': chat_request.message}]
        user_message = chat_request.message
        messages = chat_request.conversation_history + [
            {
                'role': 'user',
                'content': f"""{chat_request.message}

You are a restaurant recommendation agent. Your primary function is to help users find restaurants.

Use the 'call_restaurants_api' FUNCTION ONLY when the user explicitly expresses a desire to find a restaurant and provides specific criteria such as:

*   Cuisine (e.g., "Italian", "Mexican")
*   Dish (e.g., "pizza", "sushi")
*   Budget (e.g., "cheap", "mid-range", "expensive")

If the user provides ALL THREE criteria (cuisine, dish, and budget), you MUST call the function.

If the user provides TWO of the criteria, ask for the missing criteria.

If the user provides ONE of the criteria, ask for the other two.

If the user does not provide any of these criteria or is just having a general conversation (e.g., "Hi", "How are you?"), respond conversationally and DO NOT call the function.

Example 1 (Call the function):

User: I want to find a medium-priced Italian restaurant that serves pizza.

Assistant: (Calls call_restaurants_api with cuisine="Italian", dish="pizza", budget="medium")

Example 2 (Ask for missing criteria):

User: I'd like some Italian food.

Assistant: What kind of dish would you like, and what's your budget?

Example 3 (Conversational response):

User: Hello

Assistant: Hi there! How can I help you today?"""
            }
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "call_restaurants_api",
                    "description": "Call the restaurants API with cuisine, dish, and budget. This API call should be made only after fetching the details from the user. Do not assume the parameters.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "cuisine": {"type": "string", "description": "The type of cuisine fetched from the user."},
                            "dish": {"type": "string", "description": "The dish to search for that is fetched from the user."},
                            "budget": {"type": "string", "description": "The budget fetched from the user."},
                        },
                        "required": ["cuisine", "dish", "budget"],
                    },
                },
            }
        ]
        response = ollama.chat(model=model, messages=messages, tools=tools)

        tool_outputs = []
        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                function_name = tool_call.function.name
                # arguments = json.loads(tool_call.function.arguments) # Correctly parse arguments
                arguments = tool_call.function.arguments # Correctly parse arguments
                if function_name == "call_restaurants_api":
                    output = call_restaurants_api(**arguments)
                    tool_outputs.append({
                        "name": function_name,
                        "arguments": arguments,
                        "output": output
                    })
            chat_response_content = ""
            if tool_outputs:
                chat_response_content = json.dumps(tool_outputs[0]["output"])

        else:
            chat_response_content = response.message.content

        chat_response = {
            "response": chat_response_content,
            "tool_calls": tool_outputs,
            "conversation_history": messages + [{'role': 'assistant', 'content': chat_response_content}]
        }
        return JSONResponse(chat_response)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)