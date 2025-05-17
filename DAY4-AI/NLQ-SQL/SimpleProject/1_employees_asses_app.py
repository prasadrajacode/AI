import os
from os import linesep
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st

from langchain_ibm import WatsonxLLM  # Import WatsonxLLM from langchain_ibm
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods

# Load environment variables
load_dotenv()

params = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
    GenParams.MIN_NEW_TOKENS: 10,
    GenParams.MAX_NEW_TOKENS: 1000,
    GenParams.STOP_SEQUENCES: ['Done:"Stop here"']
}

project_id = "a15722af-476f-4ad2-ad25-090750dd14e2"  
credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": "Nt8BVcy9pRD8bDngmalyAujN02hPV7PsuJu6bpUr6zxN"
}

model_id = 'ibm/granite-20b-code-instruct'

# Initialize WatsonxLLM
llm_model = WatsonxLLM(model_id=model_id,
    url=credentials["url"],
    apikey=credentials["apikey"],
    project_id=project_id,
    params=params)

current_date = str(datetime.today().date())

SQL_PROMPT = f"Today's date is {current_date}. " + """
    
   You are a helpful assistant and IBM DB2 expert which generates SQL.
   Given an input question, create only one syntactically correct IBM DB2 query. 
   Never query for all columns from a table. 
   You must query only the columns that are needed to answer the question. 
   Pay attention to use only the column names you can see in the tables below. 
   Be careful to not query for columns that do not exist. 

   Abbreviations: 
    CY - Current Year = 2025 
    CM - Current Month = May 
    CD - Current Date = 18
    
   Context on Quarter: There are 4 quarters in a year. First quarter Q1 is from January to March. Second quarter Q2 is from April to June . Third quarter Q3 is from July to September. Fourth quarter Q4 is from October to December. 
   Use this to do all quarter calculations. 
   if Today is 06-August-2025 current quarter is Q3, Next quarter is Q4, previous quarter is Q2.
    
    Give generated SQL in following format
    Questions: 
    SQL: 
    Done:"Stop here"

    Only use the following tables:
    Table Name : GENAI.EMPLOYEES 
    Column Names, data types and meaning 
      employee_id - an integer representing the unique identifier for each employee.
      first_name - a varchar representing the first name of the employee. 
      last_name - a varchar representing the last name of the employee. 
      date_of_birth - a date representing the employee's date of birth. 
      hire_date - a date representing the date when the employee was hired. 
      department_name - a varchar representing the name of the department to which the employee belongs. 
      manager - a varchar representing the name of the employee's manager. 
      salary - an integer representing the salary of the employee. 
      email - a varchar representing the email address of the employee. 
      status - a varchar representing the employment status. Only possible values are 'Active', 'On-Leave'.

    Examples 
    Example 1:
    Input Question: Show the first name, last name and email id of all employees
    Output SQL: SELECT first_name, last_name, email FROM GENAI.EMPLOYEES;
    Done:"Stop here" 

    Example 2: 
    Input Question: Who are the employees who got hired in CY 
    Output SQL: SELECT first_name, last_name, email FROM GENAI.EMPLOYEES WHERE hire_date > '2025-01-01'; 
    Done:"Stop here" 

    Example 3:
    Input Question: Give me the list of employees who got hired in the previous quarter 
    Output SQL: SELECT first_name, last_name, email FROM GENAI.EMPLOYEES WHERE hire_date > '2025-04-01' AND hire_date < '2025-07-01'; 
    Done:"Stop here" 
    
    Question: {input}   
"""

def run_llm(question):
    prompt = SQL_PROMPT.format(input=question)
    prompts = [prompt]
    
    response = llm_model.generate(prompts)  

    # Accessing the generations attribute of the LLMResult object
    generations = response.generations
    generation_obj = generations[0][0]  
    sql_query = generation_obj.text.strip()
    sql_query = sql_query.replace("\t", " ").replace("\n", " ")
    if "Done-\"Stop here\"" in sql_query:
        sql_query = sql_query.replace("Done-\"Stop here\"", "").strip()
    
    return sql_query

# Streamlit app UI
st.title('IBM DB2 Query Generator from NLQ')

# Sample Questions
st.subheader("Sample SQL Queries:")
st.write("""
1. **Show the first name, last name, and email id of all employees?**

2. **Give me the employee details who report to David?**

3. **How many employees are born after the year 2000?**

4. **Who are the employees who got hired in CY?**  
   (Note: CY stands for Current Year)

5. **Give me employees details who are above 50 this year?**

6. **Show the date of birth and hire date of employees who were hired in 1992, quarter 2?**

7. **Show me the details for employee with ID 101?**

8. **List the employees who belong to the Sales department and are on leave?**

9. **Show the department names along with the count of employees in each department?**

10. **Display the employee ID, first name, last name, and salary for employees who earn between $60,000 and $80,000?**

11. **Give me the list of employees who got hired in the previous quarter?**
""")

# Input box for the question
question = st.text_input('Enter your question:')

if st.button('Generate SQL'):
    if question:
        st.write(f'Question: {question}')
        
        # Generate SQL query
        start = datetime.now()
        sql_query = run_llm(question)
        end = datetime.now()

        # Display the generated SQL
        st.subheader('Generated SQL:')
        st.code(sql_query, language='sql')

        #st.write(f'Total execution time: {end-start}')
    else:
        st.warning('Please enter a question before clicking "Generate SQL".')

