from llm_model import generate

def call_weather_api(city):
    if city.lower() == "paris":
        return "The weather in Paris is sunny with a temperature of 22°C."
    return f"No weather data available for {city}."

city = "Paris"
observation = call_weather_api(city)

# Stronger prompt format
prompt = f"""
You are a reasoning assistant. Follow the ReACT format exactly as shown.

Always respond in this structure:
Question: <user question>
Thought 1: <your plan>
Action 1: <function call>
Observation 1: <result of that function>
Thought 2: <analyze the result logically and summarize it>
Final Answer: <use the observation to answer the question>

Be specific in Thought 2. Do not just say "The observation tells me..." — instead, rephrase and reason about the result.

Example:
Question: What is 5 + 2?
Thought 1: I need to add 5 and 2.
Action 1: add(5, 2)
Observation 1: 7
Thought 2: The result of the addition is 7.
Final Answer: 5 + 2 = 7.

---

Question: What is the weather in {city}?
Thought 1: I need to find the weather in {city}.
Action 1: call_weather_api("{city}")
Observation 1: {observation}
Thought 2:"""




response = generate(prompt, max_tokens=200)
print("LLM Response:\n", response)
