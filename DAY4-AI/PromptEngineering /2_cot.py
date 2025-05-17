from llm_model import generate

prompt1 = """
I went to the market and bought 10 apples. 
I gave 2 apples to the neighbor and 2 to the repairman. 
I then went and bought 5 more apples and ate 1.
How many apples did I remain with?

Answer:
"""
#this gives wrong answer 


prompt2 = """
I went to the market and bought 10 apples.
I gave 2 apples to the neighbor and 2 to the repairman. 
I then went and bought 5 more apples and ate 1. 
How many apples did I remain with?
Let's think step by step in a logical manner calculating in each step.
Please show your reasoning before giving the final answer by breaking down the question into steps.

Answer: 
"""

prompt3 = """
If a train leaves at 3 PM and takes 4 hours to reach the destination, what time does it arrive?
Let's think step-by-step in a logical manner.
Please show your reasoning before giving the final answer by breaking down the question into steps. Dont provide any other additional information. 

Answer:
"""

prompt4 = """
If there are 3 red balls and 2 blue balls in a bag, and you take one out at random, what's the chance it's red? 
Let's think step by step in a logical manner.
please show your reasoning before giving the final answer by breaking down the question into steps. Dont provide any other additional information. 

Answer:
"""

#print(generate(prompt1))
#print(generate(prompt2))
#print(generate(prompt3))
print(generate(prompt4))