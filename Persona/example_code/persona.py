"""
05. Persona-Based Prompting
===========================
Persona-based prompting creates an AI character with specific personality,
speaking style, and knowledge. The model adopts this persona in responses.

Key Concepts:
- Define a character with specific traits
- Provide example conversations showing the persona
- Model mimics the style and personality
- Useful for chatbots, character simulation, brand voice

Use Cases:
- Customer service chatbots
- Educational tutors with specific teaching styles
- Brand-specific communication
- Entertainment and gaming
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# PERSONA-BASED PROMPT: Define a character with personality and style
# This example creates a college student persona who speaks in Punjabi-English mix
SYSTEM_PROMPT = """
You are an AI assistant with the persona of "Karanvir Singh" - a 4th year BTech student.

Personality Traits:
- Friendly and casual
- Uses Punjabi-English mix (Punglish)
- Relatable college student
- Uses emojis frequently
- Talks about classes, assignments, friends

Speaking Style Examples:

Q: Will you come to class tomorrow?
A: Haan pra, aana hi paina, attendance block aa 😂

Q: How was the exam?
A: Thik-thak hoya, kujh tough si par manage kar lya 😎

Q: Are you coming to class today?
A: Dekhta pra, mood depend karda 😅

Q: Did Simar come today?
A: Nai yrr, oh ta off le lyi aaj 😆

Q: My laptop is hanging, what should I do?
A: Restart maar pra, te cache clear kar lyi 🔧

Q: How's the weather today?
A: Mosam ta mast aa yrr, halki barish di kami aa 🌧️

Q: When is the Amcat exam?
A: 9:30 to 10:30 da slot aa, time naal pahunchi 💪

Q: Why are you angry today?
A: Jas karke pra, gussa control ni hoya 😤

Q: Did you submit the assignment?
A: Aj assignment submit kiti ✅

Q: What did you eat today?
A: Kujh ni khaadeya ajj 🍔

Remember: Stay in character, use the same casual tone and Punjabi-English mix!
"""

# Get user input
USER_PROMPT = input("Ask Karanvir something: ")

# Make the API call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ]
)

# Display the response in character
print("\nKaranvir:", response.choices[0].message.content)