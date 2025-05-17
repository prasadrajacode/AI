from llm_model import generate

_prompt = f"""
You are a reasoning assistant following the Tree of Thoughts (ToT) method. Break down your reasoning into multiple layers of thoughts.

Use this exact structure:
Question: <question>
Thought 1: <first step or initial idea>
    Sub-thought 1.1: <sub-step or reasoning of step 1>
    Sub-thought 1.2: <sub-step or reasoning of step 1>
Thought 2: <next step or deeper reasoning>
    Sub-thought 2.1: <sub-step or reasoning of step 2>
    Sub-thought 2.2: <sub-step or reasoning of step 2>
...
Final Answer: <final answer based on all thoughts>

Ensure that each "Thought" breaks into sub-thoughts. You must structure your reasoning in a tree-like manner.

Example:
Question: What is 5 + 3?
Thought 1: I need to add 5 and 3.
    Sub-thought 1.1: The first number is 5.
    Sub-thought 1.2: The second number is 3.
Thought 2: I will perform the addition.
    Sub-thought 2.1: 5 + 3 equals 8.
Final Answer: 5 + 3 = 8.

---

Question: If a train leaves at 3 PM and takes 4 hours, what time does it arrive?
Thought 1: I need to calculate the time of arrival.
    Sub-thought 1.1: The departure time is 3 PM.
    Sub-thought 1.2: The duration of the trip is 4 hours.
Thought 2: Add 4 hours to 3 PM.
    Sub-thought 2.1: Adding 4 hours to 3 PM gives 7 PM.
Final Answer: The train arrives at 7 PM.
"""


# Simulate external weather API function
def call_weather_api(city):
    if city.lower() == "paris":
        return "It is sunny with a temperature of 22°C."
    return f"Weather data for {city} is unavailable."

# Function to generate a Tree of Thoughts-style prompt
def generate_tree_of_thoughts_prompt(city, observation):
    return f"""
You are a reasoning assistant following the Tree of Thoughts format. Break down your reasoning into distinct steps. Each step leads to the next logical sub-step, and you'll take actions based on these steps.

Question: What is the weather in {city}?

Thought 1: I need to figure out what the weather in {city} is.
    Sub-thought 1.1: First, I will check the current weather for {city}.
    Sub-thought 1.2: To do this, I will call the weather API with {city} as the city.
Action 1: call_weather_api("{city}")
Observation 1: {observation}

Thought 2: I can now use the observation to understand the weather in {city}.
    Sub-thought 2.1: The observation says the weather is sunny.
    Sub-thought 2.2: The temperature is 22°C, which gives me all the weather information I need.

Final Answer: The weather in {city} is sunny with a temperature of 22°C.
"""

# Example usage
city = "Paris"
observation = call_weather_api(city)  # Simulate calling the weather API

# Generate the prompt based on the observation
prompt = generate_tree_of_thoughts_prompt(city, observation)

# Assuming `generate()` is a function that interfaces with the model
response = generate(prompt, max_tokens=200)

print("LLM Response:\n", response)

