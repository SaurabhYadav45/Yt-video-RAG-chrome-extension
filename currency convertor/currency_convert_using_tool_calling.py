import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
import requests
from langchain_core.tools import InjectedToolArg
from typing import Annotated
# https://colab.research.google.com/drive/1-xMYU9ExZqoySEX-XHAvEaE17PCWvc9H?usp=sharing
load_dotenv()

EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")


@tool
def get_conversion_factor(base_currency:str, target_currency:str)->str:
    """ This function fetches the Currency conversion factor between a given base currecny and target currency """

    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair/{base_currency}/{target_currency}"

    response = requests.get(url)
    return response.json()

@tool
def convert(base_currency_value:int, conversion_rate:Annotated[float, InjectedToolArg])->float:
    """ This function takes base currency value and conversion rate and convert the base currency value to target currency value """

    return base_currency_value * conversion_rate


# print(convert.args)

# res = get_conversion_factor.invoke({'base_currency':'USD', 'target_currency':'INR'})
# print(res)

# res2 = convert.invoke({'base_currency_value':10, 'conversion_rate':85})
# print(res2)

llm = ChatOpenAI()

llm_with_tools = llm.bind_tools([get_conversion_factor, convert])

query = HumanMessage("hat is the conversion factor between INR and USD, and based on that can you convert 10 USD to INR")
messages = [query]

ai_message = llm_with_tools.invoke(messages)
# print("\nAI Message: ", ai_message)

messages.append(ai_message)

# print("\nTool Calls: ", ai_message.tool_calls)

# Tool Execution
for tool_call in ai_message.tool_calls:
    if tool_call['name'] == 'get_conversion_factor':
        tool_message1 = get_conversion_factor.invoke(tool_call)
        # print("\ntool_message1: ",tool_message1)
        conversion_rate = json.loads(tool_message1.content)['conversion_rate']
        messages.append(tool_message1)
    
    if tool_call['name'] == 'convert':
        tool_call['args']['conversion_rate'] = conversion_rate
        tool_message2 = convert.invoke(tool_call)
        messages.append(tool_message2)

response = llm_with_tools.invoke(messages)
print("\nFinal result: ", response.content)
