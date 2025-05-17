import os
from os import linesep
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
import time

from langchain_ibm import WatsonxLLM  # Import WatsonxLLM from langchain_ibm
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods

load_dotenv()

params = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
    GenParams.MIN_NEW_TOKENS: 10,
    GenParams.MAX_NEW_TOKENS: 1000,
    GenParams.STOP_SEQUENCES: ['Done-"Stop here"'],
    # GenParams.TEMPERATURE: 0.2,
}

project_id = os.getenv("PROJECT_ID", None)  
credentials = {
    "url": os.getenv("URL"),
    "apikey": os.getenv("APIKEY")
}

model_id = 'ibm/granite-20b-code-instruct'

# Initialize WatsonxLLM instead of Model
llm_model = WatsonxLLM(model_id=model_id,
    url=credentials["url"],
    apikey=credentials["apikey"],
    project_id=project_id,
    params=params)

current_date = str(datetime.today().date())

SQL_PROMPT = f"Today's date is {current_date}. " + """
   Given an input question, create a syntactically correct IBM DB2 query.
    
   Abbreviations:                   
    CM -Current Month 
    
   Table definition:    
    - Table Name - GENAI.ORDERS    
    - Columns     
    ORDER_ID - number - 6 digit unique identification code for Orders.
    ORDER_DATE - date - date on which the order is placed.
    REQUESTED_DELIVERY_DATE - date - Date on which the customer requested for delivery.
    CUSTOMER_NAME - text - Customer name.
    SHIPMENT_GEO- text - Customer geo region name. Strictly use only the possible values in the filter.
    PRODUCT_NAME - text - Product Name.
    SEGMENT - text - Product Category.
    ORDER_QTY - number - Order Quantity.
    ORDER_AMOUNT - decimal - Total Order amount.
    
    Possible Values: 
    SHIPMENT_GEO values can only be AMERICAS, JAPAN, ASIA, EUROPE
    SEGMENT values can only be Consumer, Corporate, Home Office
    
    Rules:
    Ensure that the SQL query is concise and do not repeat the column names.
    When generating month or quarter filter, do include year and month filters.
    Use like operator to match customer names and product names in the filter.
    Use upper function for columns in where clause to match the filter values.  
    When generating filters, strictly use only possible values for SHIPMENT_GEO and SEGMENT.
    Use only IBM DB2 compatible date functions.
    
    Format the generated SQL output as follows:
    Question-
    SQL-  
    Done-"Stop here" 

    Examples:    
    Example 1.
    Question- Show me the orders for Joe in Quarter 3 2021 for USA?
    SQL-  SELECT ORDER_ID, ORDER_DATE, REQUESTED_DELIVERY_DATE, CUSTOMER_NAME, SHIPMENT_GEO, PRODUCT_NAME, SEGMENT, ORDER_QTY, ORDER_AMOUNT
    FROM GENAI.ORDERS    
    WHERE UPPER(CUSTOMER_NAME) LIKE '%JOE%'
    AND YEAR(ORDER_DATE) = 2021 AND QUARTER(ORDER_DATE) = 3 
    AND UPPER(SHIPMENT_GEO) = 'AMERICAS'
    ORDER BY ORDER_AMOUNT DESC
    Done-"Stop here"
    
    Question- {input}   
"""

def run_llm(question):
    prompt = SQL_PROMPT.format(input=question)
    #print("Prompt:", prompt)
    prompts = [prompt]
    
  
    response = llm_model.generate(prompts)  

    # Accessing the generations attribute of the LLMResult object
    generations = response.generations
    generation_obj = generations[0][0]  
    sql_query = generation_obj.text.strip()
    sql_query = sql_query.replace("\t", " ").replace("\n", " ")
    if "Done-\"Stop here\"" in sql_query:
        sql_query = sql_query.replace("Done-\"Stop here\"", "").strip()
    print(sql_query) 
if __name__ == '__main__':
    start = datetime.now()
    nlq = "show me orders for last week?"
    
    print(f'Question : {nlq}')
    run_llm(question=nlq)
    end = datetime.now()

    print(f'Total time of execution {end-start}')
