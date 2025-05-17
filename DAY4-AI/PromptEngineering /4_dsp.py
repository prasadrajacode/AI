"""
This files uses dynamic prompt generation to call LLM 
"""

from llm_model import generate

def build_prompt(name, topic):
    return f"Hello {name}, today we're going to learn about {topic}. Can you explain it in simple words?"

# Dynamic prompt generation
user_name = "Alex"
user_topic = "Deep learning"

prompt = build_prompt(user_name, user_topic)
print(prompt)

response = generate(prompt)

# Output the result
print("Response:", response)