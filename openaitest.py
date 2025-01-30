import openai
from dotenv import load_dotenv
from typing_extensions import override
from openai import AssistantEventHandler

load_dotenv()

# openai.api_key = os.environ.get("OPEN_API_KEY")

client = openai.OpenAI()

model = "gpt-4o"


# personal_assist = client.beta.assistants.create(
#     name="Personal Trainer",
#     instructions="You are the best personal trainer and nutritionist who knows how to get clients to build lean muscles.you've trained high-caliber athletes and movie stars.",
#     tools=[{"type": "code_interpreter"}],
#     model=model,
# )

# assistant_id = personal_assist.id
# print(assistant_id)

# thread = client.beta.threads.create( messages=[
#     {
#         "role" : "user",
#         "content" : " How do I get started working out to lose fat and gain muscles"
#     }
# ] )

# thread_id = thread.id

# print(thread_id)

# --- Hardcode ID
assistant_id = 'asst_418i6ikKLjIf8spDMfwnm4As'
thread_id = 'thread_PVA3BZBpnghBpu9ZmeWVvAMo'


# === Create a Message ===

message = "What are the best exerciese for lean muscles"

message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=message
)

#== Run assistant

# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > on_text_created", end="", flush=True)


    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)


    def on_tool_call_created(self, tool_call):
        print(f"\nassistant tool > {tool_call.type}\n", flush=True)


    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == "code_interpreter":
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput code >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)


# Then, we use the `stream` SDK helper
# with the `EventHandler` class to create the Run
# and stream the response.

with client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions="Please address the user as Jane Doe. The user has a premium account.",
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()


