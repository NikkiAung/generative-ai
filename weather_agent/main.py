from openai import OpenAI
import requests
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def get_weather(city: str) -> str:
    """Fetch real-time weather data using the free wttr.in API."""
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text.strip()}"  # ✅ Fix 1: use the `city` variable
    else:
        return "Weather information not available"


def main():
    print("=" * 50)
    print("   Simple Weather Chatbot")
    print("=" * 50)

    user_query = input("\nAsk me about any city's weather: ")  # ✅ Fix 2: clear prompt label

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful weather assistant. When the user asks about weather, reply helpfully."
            },
            {
                "role": "user",
                "content": user_query
            }
        ]
    )

    print("\nAssistant:", response.choices[0].message.content)


if __name__ == "__main__":  # ✅ Fix 3: proper __main__ guard so nothing runs on import
    main()