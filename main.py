from agents import Agent, Runner, OpenAIChatCompletionsModel, RunConfig, set_tracing_disabled, function_tool, handoff, AsyncOpenAI, RunContextWrapper
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client_provider = AsyncOpenAI(
    api_key = GEMINI_API_KEY,
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(model ="gemini-2.0-flash", 
                                   openai_client = client_provider)
set_tracing_disabled(True)

config = RunConfig(
    model = model, 
    model_provider = client_provider, 
    tracing_disabled = True)

class User_info(BaseModel):
    name: str
    email: str
    order_id: int

# get_user_info = function_tool(
    
billing_Agent = Agent(
    name = "Billing_Support_Agent",
    instructions = "You are a billing support, answer question related to billing payments and invoices. If you don't know answer say I don't Know."
)
technical_agent = Agent(
    name = "Technical_Support_Agent",
    instructions = "You are a technical support agent, answer question related to technical issue, Trobleshooting and productive futures, if you don't know say i don't Know."
)
general_agent = Agent(
    name = "General_support_agent",
    instructions = "you are a general support agent, answer general questions about the company, products and services. if you don't know say i don't Know."
)
triage_agent = Agent(
    name = "Triage_Agent",
    instructions = "You are a triage agent. Your job is to datermine the type of support needed and hand off to the appropriate agent. If you don't know the answer, say 'I don't know'.",
    handoffs = [billing_Agent, technical_agent, general_agent]
) 

User_Question = input("What is your question Ask Please....")

result = Runner.run_sync(
    triage_agent,
    User_Question,
    run_config = config
)

print(result.final_output)
