# Approach Results

## step-1
Run the main.py file in one terminal with the following command
> python -m uvicorn main:app --port 8003

## step-2
Run the api_zomato.py file in another terminal with the following command
> python api_zomato.py

## step-3
Run the curl command to hit the chat api 
**'http://localhost:8003/chat'**

### Results


> curl -X POST 'http://localhost:8003/chat' -H "Content-Type: application/json" -d '{"message": "hi"}'

> {"response":"Hello! I'm Marco, your food assistant. I'm here to help you discover delicious meals. To get started, could you please tell me the name of the dish you are interested in?\n"}

> curl -X POST 'http://localhost:8003/chat' -H "Content-Type: application/json" -d '{"message": "pizza"}'

> {"response":"Great! Now, is this meal for vegetarians or non-vegetarians?\n"}

> curl -X POST 'http://localhost:8003/chat' -H "Content-Type: application/json" -d '{"message": "veg"}'

> {"response":"Perfect. What is your budget in rupees for this meal?\n"}

> curl -X POST 'http://localhost:8003/chat' -H "Content-Type: application/json" -d '{"message": "300"}'

> {"response":"And finally, how many people should this meal serve?\n"}

> curl -X POST 'http://localhost:8003/chat' -H "Content-Type: application/json" -d '{"message": "2"}'

> {"response":[{"id":1,"name":"Italian Delight","city":"New York","cuisine":"vegetarian","dishes":["Pasta","Pizza","Tiramisu"],"budget":300},{"id":9,"name":"Pizzeria Napoli","city":"Naples","cuisine":"vegetarian","dishes":["Pizza","Pasta","Caprese Salad"],"budget":250}]}
