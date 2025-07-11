from langchain.tools import  StructuredTool
from pydantic import BaseModel, Field

class MultiplyInput(BaseModel):
    a:int = Field(required=True, description="the first number to add")
    b:int = Field(required=True, description="the second number to add")

def multiply_fun(a:int, b:int)->int:
    return a*b

multiply_tool  = StructuredTool.from_function(
    func=multiply_fun,
    name="Multiply",
    description="multiply two numbers",
    args_schema=MultiplyInput
)

res2 = multiply_tool.invoke({"a":5, "b":6})
print(res2)
print(multiply_tool.name)
print(multiply_tool.description)
print(multiply_tool.args)