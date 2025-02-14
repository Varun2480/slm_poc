import os
import requests
from google.ai.generativelanguage_v1beta.types import content
import google.generativeai as genai
from typing import Optional, List, Dict
from pydantic import BaseModel
from fastapi import FastAPI, Request
from google.generativeai.types import Tool as ToolDeclaration, FunctionDeclaration

class ChatRequest(BaseModel):
    message: str

app = FastAPI()

conversation_histories = {}  # Store histories by user ID or session ID

@app.post("/chat")
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    user_id = "varun"  # Replace with your user identification logic
    history = conversation_histories.get(user_id, [])

    user_input = chat_request.message
    response, updated_history = get_gemini_response(user_input, history)

    conversation_histories[user_id] = updated_history  # Update history for the user

    return {"response": response}

def call_restaurants_api(cuisine: str, dish: str, budget: str):
    """Call the restaurants API."""
    url = "http://127.0.0.1:8002/restaurants/search"
    payload = {"cuisine":cuisine,"dish":dish,"budget":budget}  # Use passed arguments
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        return response.json()  # Return JSON
    else:
        return f"API request failed with status code: {response.status_code}"


def call_external_api(data: str) -> str:
    """
    Calls an external API running on port 8003.

    Args:
        data: The data to send to the external API.

    Returns:
        The response from the external API.
    """
    try:
        response = requests.post("http://localhost:8003/your_api_endpoint", json={"data": data})
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()["result"]  # Assuming the API returns a JSON with a 'result' field
    except requests.exceptions.RequestException as e:
        return f"Error calling external API: {e}"
    
# Function declaration for the tool
function_declaration = {
    "name": "call_external_api",
    "description": "Calls an external API running on port 8003 with the provided data.",
    "parameters": {
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "description": "The data to send to the external API.",
            },
        },
        "required": ["data"],
    },
}

function_declaration = FunctionDeclaration(
    name='call_restaurants_api',
    description='Calls the restaurants API to search for restaurants based on cuisine, dish, and budget.',
    parameters={
        'type': 'object',  # Add "type": "object" here
        'properties': {
            'cuisine': {
                'type': 'string',
                'description': 'The type of cuisine (e.g., Italian, Indian, Mexican).',
            },
            'dish': {
                'type': 'string',
                'description': 'The name of the dish (e.g., pizza, pasta, biryani).',
            },
            'budget': {
                'type': 'string',  # Or "number" if you expect a numerical budget
                'description': 'The budget for the meal (e.g., 300, 500).',
            },
        },
        'required': ['cuisine', 'dish', 'budget'],
    }
)


def get_gemini_response(user_input, history=[]):  
    """
    Interacts with the Gemini model, including history, and returns the response.

    Args:
        user_input: The user's current query or message.
        history: A list of previous messages in the conversation.

    Returns:
        The Gemini model's response as a string, and the updated history.
    """
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    # Create the model
    generation_config = {
      "temperature": 1,
      "top_p": 0.95,
      "top_k": 64,
      "max_output_tokens": 8192,
      "response_mime_type": "text/plain",
    }
    
    model = genai.GenerativeModel(
      model_name="gemini-2.0-flash-lite-preview-02-05",
      generation_config=generation_config,
      system_instruction="You are Marco, a food assistant specializing in helping users discover meals based on their preferences. Your primary role is to gather key information about the user's needs, including the food name, type (vegetarian or non-vegetarian), budget (in rupees only), and the number of people it should serve. You must ask one question at a time, keeping queries precise and to the point. Once all the information is collected, you will use the integrated API to provide meal options based on the user's preferences. Greet users with a warm and friendly welcome message to start each interaction. Your tone should be approachable yet concise, ensuring the conversation remains efficient. The currency used for ordering will always be rupees, and no other currency context should be considered.",
    #   tools = [
    #     genai.protos.Tool(
    #       function_declarations = [function_declaration],
    #     ),
    #   ],
    tools=[ToolDeclaration(function_declarations=[function_declaration])],
    )
    
    chat_session = model.start_chat(history=history)  # You might adjust history handling
    response = chat_session.send_message(user_input)

    data = response.to_dict()
    
    # Check for tool calls within the dictionary
    if data.get("candidates") and data["candidates"][0].get("content") and data["candidates"][0]["content"].get("parts"):
        for part in data["candidates"][0]["content"]["parts"]:
            if part.get("function_call"):
                function_name = part["function_call"]["name"]
                arguments = part["function_call"]["args"]

                if function_name == "call_restaurants_api":
                    external_api_response = call_restaurants_api(**arguments)
                    # ... (Incorporate external API response as needed) ...

                    # Add tool call to history
                    history.extend([
                        {"role": "tool_code", "parts": [external_api_response]},
                    ])

                    return external_api_response, history


    history.extend([
        {"role": "user", "parts": [user_input]},  # User message
        {"role": "model", "parts": [response.text]},  # Model response
    ])

    return response.text, history
