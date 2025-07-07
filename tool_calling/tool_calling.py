from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
import requests

@tool
def multiply(a:int, b:int)->int:
    """This tool returns the multiplication of two numbers"""
    return a*b

# res = multiply.invoke({'a':18, 'b':12})
# print(res)

llm = ChatOpenAI()

# Tool binding
llm_with_tool = llm.bind_tools([multiply])
# res2 = llm_with_tool.invoke("Hii how are you")
# print(res2)

query = HumanMessage("Multiply 13 and 11")
message = [query]

result = llm_with_tool.invoke(message)
# print("Result: ", result)
# print("Tool calls: ", result.tool_calls)
print("Tool call des: ", result.tool_calls[0])
message.append(result)
# print("Message: ", message)


# TOOL Execution
tool_result = multiply.invoke(result.tool_calls[0])
print("Tool Result: ", tool_result)

message.append(tool_result)

response = llm_with_tool.invoke(message)
print("\nFinal response: ", response.content)
