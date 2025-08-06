import os
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, RunConfig, RunContextWrapper, function_tool, Handoff
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, Any, List
from dataclasses import dataclass

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY"),
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in .env file.")
    
provider = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider
)

run_config = RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True
)

class userInfo(BaseModel):
    name: str
    is_premium: bool
    issue_type: Optional[str] = None

@dataclass
class productinfo:
    product_name: str
    product_price: int
    product_quantity: int
    product_description: str


@function_tool
async def satationary_items(wrapper: RunContextWrapper, user: userInfo) -> List[productinfo]:
    """
    Provide information about stationary products.
    """
    return [
        productinfo(
            product_name="Notebook",
            product_price=50,
            product_quantity=100,
            product_description="A5 size notebook with 200 pages."
        ),
        productinfo(
            product_name="Pen",
            product_price=10,
            product_quantity=500,
            product_description="Blue ink ballpoint pen."
        ),
        productinfo(
            product_name="Pencil",
            product_price=5,
            product_quantity=300,
            product_description="HB wooden pencil with eraser."
        ),
    ]
@function_tool(
        is_enabled= lambda self, context: isinstance(context, (RunContextWrapper, userInfo)) and context.is_premium
)
def refund_tool(wrapper: RunContextWrapper[userInfo]) -> str:

    """
    Processs a refund for the user.
    """
    if not wrapper.context.is_premium:
        return "Error: This tool is only available for premium users."
    return f"Refund processed for {wrapper.context.name} (premium user)."
@function_tool
async def restart_service(wrapper: RunContextWrapper[userInfo]) -> str:
    """
    Restart the service for the Technical Issues.
    """
    return f"Service restarted for {wrapper.context.name}."

class TechnicalGuardrailOutput(BaseModel):
    is_correct_routing: bool
    reasoning: str
    expected_agents: str
    restart_service: bool

guardrail_agent = Agent(
    name="Technical Guardrail Agent",
    instructions=(
    "Inalyze the outtput of the support agent to datermine if it correctly handleds technical quarys."
    "if the user query should indicate a handoff to the technical agent"
    "and the restarted service should be called."
    "Return weather the routing is correct, the reasoning, the expected agents, and whether restarted service was called."
),
    output_type =TechnicalGuardrailOutput,
    model=model,
)

@output_guardrail
async def technical_guardrail(
    ctx: RunContextWrapper[userInfo],
    agent: Agent,
    output: str)  -> GuardrailFuncationOutput:
    user_quary_issue_type = ctx.context.issue_type if ctx.context else "unone"
    result = await Runner.run(
        guardrail_agent,
        input=f"User Quary Issue Type: {user_quary_issue_type}\n support agent output: {output}",
        run_config=run_config,
        context=ctx.context
    )

    tripwire_triggered = False
    if user_quary_issue_type == "technical",
        if not result.output.is_correct_routing or not result.output.restart_services called:
            tripwire_triggered = True

    return GuardrailFuncationOutput(
        output_info=result.output,
        tripwire_triggered=tripwire_triggered,
    )
Item_Info_agents = Agent(
    name="Item Info Agent",
    instructions="handle user queries releated to product names, quantity, price, and discripation.",
    "use the stationary_items tool to retrieve information about stationary product details and answer the users queries."
    tools=[satationary_items],
    model=model,
)

billing_agent = Agent(
    name="Billing Agent",
    instructions="Handle billing related queries, inccluding resfunds for the premium users."
    "Use the refund_tool to process refunds when appropriate."
    "if the user is not a premium user, politely say this future this future is only for premium users.",
    tools=[refund_tool],
    model=model,
)
technical_agent = Agent(
    name="Technical Agent",
    instructions="Handle technical queries, such as service outages or errors."
    "use the restart_service tool to restart the service when appropriate.",
    tools=[restart_service],
    model=model,
)

support_agent = Agent(
    name="Support Agent",
    instructions="Handle all user queries",
    "for refunds related queries, hand off to the billing agent.",
    "for product information queries, (e.g., product name, price, quantity, discription) hand off to the Item_Info_agents.",
    "for technical queries, (e.g., service issues, errors,) hand off to the technical_agent.",
    "if the user is not a premium user and requests a refund, politely say this future is only for premium users.",
    handoffs=[Item_Info_agents, billing_agent, technical_agent],
    model=model,
)

async def main():
    context = userInfo(
        name="Sharmeen Fatima",
        is_premium=False,
    )


print(support_agent)
print("type quit to exit")\n
    while True:
        prompt = input("Enter your question: ")
        if prompt.lower() == "quit":
            print("Goodbye!")
            break

        if "refund" in prompt.lower():
            user.context.issue_type = "billing"
        elif Any(keyword in prompt.lower() for keyword in ["technical", "service", "error, restart"]):
        else:
        user context.issue_type = "product"

        print(f"issue type: detected")
        print(processing your request...)
        result = Runner.run_stream(
            support_agent,
            input prompt,
            run_config=run_config,
            context=user context
        )

        try: 
            print("agent:", and "" , flush=True)
            async for event in result.streamevents:
                if event.type == "row response event" and isinstance(event.data, ResponseTextDataEvent):
                    print("event:", event.data.dalta, flush=True)

            final_result = result
            if final_result.final_output:
                print(f"final response: {final_result.final_output}")

    else: 
        print("no final output received.")
    except outputgraduriltriwire_triggered as e:   
        print(f"Tripwire triggered: {e}")
        
        # result = await Runner.run(
        #     support_agent,
        #     prompt,
        #     run_config=run_config,
        #     context=user_context
        # )

        # print(result.final_output)








# billing_agent = Agent(
#     name="Billing Support Agent",
#     instructions="You are a billing support agent. Answer questions related to billing, payments, and invoices. If you don't know the answer, say 'I don't know'.",
#     tools=[umfat_billing_info],
# )

# technical_agent = Agent(
#     name="Technical Support Agent",
#     instructions="You are a technical support agent. Answer questions related to technical issues, troubleshooting, and product features. If you don't know the answer, say 'I don't know'.",
#     tools=[Umfat_technical_info],
# )

# general_agent = Agent(
#     name="General Support Agent",
#     instructions="You are a general support agent. Answer general questions about the company, products, and services. If you don't know the answer, say 'I don't know'.",
#     tools=[Umfat_general_info],
# )

# triage_agent = Agent(
#     name="Triage Agent",
#     instructions="You are a triage agent. Your job is to datermine the type of support needed and hand off to the appropriate agent. If you don't know the answer, say 'I don't know'.",
#     handoffs=[billing_agent, technical_agent, general_agent]
# )

# context = userInfo(
#     name="Sharmeen Fatima",
#     email="sharmeen.fatima@example.com",
#     order_id=410636
# )
# prompt = input("Enter your question: ")

# result = Runner.run_sync(
#     triage_agent,
#     prompt,
#     run_config=run_config,
# )

# print(result.final_output)