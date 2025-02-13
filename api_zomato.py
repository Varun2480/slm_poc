from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel

app = FastAPI()

# Dummy restaurant data
restaurants = [
    {"id": 1, "name": "Italian Delight", "city": "New York", "cuisine": "Italian", "dishes": ["Pasta", "Pizza", "Tiramisu"], "budget": "medium"},
    {"id": 2, "name": "Tokyo Sushi", "city": "Los Angeles", "cuisine": "Japanese", "dishes": ["Sushi", "Ramen", "Tempura"], "budget": "high"},
    {"id": 3, "name": "Delhi Spice", "city": "New York", "cuisine": "Indian", "dishes": ["Curry", "Biryani", "Naan"], "budget": "medium"},
    {"id": 4, "name": "Paris Bistro", "city": "Paris", "cuisine": "French", "dishes": ["Crepe", "Steak Frites", "Croissant"], "budget": "high"},
    {"id": 5, "name": "Mumbai Bites", "city": "Mumbai", "cuisine": "Indian", "dishes": ["Vada Pav", "Pav Bhaji", "Misal Pav"], "budget": "low"},
    {"id": 6, "name": "Hyd Biryani House", "city": "Hyderabad", "cuisine": "Indian", "dishes": ["Biryani", "Haleem", "Kebabs"], "budget": "medium"},
    {"id": 7, "name": "The Greek Taverna", "city": "Athens", "cuisine": "Greek", "dishes": ["Souvlaki", "Moussaka", "Gyros"], "budget": "low"},
    {"id": 8, "name": "Berlin Schnitzel Haus", "city": "Berlin", "cuisine": "German", "dishes": ["Schnitzel", "Sausage", "Pretzel"], "budget": "medium"},
    {"id": 9, "name": "Pizzeria Napoli", "city": "Naples", "cuisine": "Italian", "dishes": ["Pizza", "Pasta", "Caprese Salad"], "budget": "low"},
    {"id": 10, "name": "Chennai Express", "city": "Chennai", "cuisine": "Indian", "dishes": ["Dosa", "Idli", "Uttapam"], "budget": "low"},
]


# 1. Restaurants Listing by City
@app.get("/restaurants/{city}")
def get_restaurants_by_city(city: str) -> List[Dict]:
    """Returns a list of restaurants in a given city."""
    city_restaurants = [restaurant for restaurant in restaurants if restaurant["city"] == city]
    if not city_restaurants:
        raise HTTPException(status_code=404, detail=f"No restaurants found in {city}")
    return city_restaurants

class RestaurantSearch(BaseModel):
    cuisine: Optional[str] = None
    dish: Optional[str] = None
    budget: Optional[str] = None

# 2. Restaurants by Cuisine, Dish, and Budget
@app.post("/restaurants/search")
def search_restaurants(search_params: RestaurantSearch) -> List[Dict]:
    """Searches for restaurants based on cuisine, dish, and budget."""

    filtered_restaurants: List[Dict] = []  # Initialize an empty list

    for restaurant in restaurants:
        if search_params.cuisine and restaurant["cuisine"].lower() != search_params.cuisine.lower():
            continue  # Skip to the next restaurant if cuisine doesn't match

        if search_params.dish:
            dish_found = False
            if restaurant["dishes"]:
                for dish in restaurant["dishes"]:
                    if search_params.dish.lower() in dish.lower():
                        dish_found = True
                        break # Exit inner loop once dish is found
            if not dish_found:
                continue  # Skip if dish is not found

        if search_params.budget and restaurant["budget"].lower() != search_params.budget.lower():
            continue  # Skip if budget doesn't match

        filtered_restaurants.append(restaurant)  # Add the restaurant to the filtered list

    if not filtered_restaurants:
        raise HTTPException(status_code=404, detail="No restaurants found matching your criteria")

    return filtered_restaurants

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)