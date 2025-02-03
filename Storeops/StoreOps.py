
import openai
import os
import requests
import json
import time
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import numpy as np


load_dotenv()

# Load library and model
client = openai.OpenAI()
model = "gpt-4o"

# Load news api
news_api_key = os.environ.get("NEWS_API_KEY")

results = []


def get_sales(topic):
    print(f"----> LOG {topic}")
    url = (f"http://192.168.3.61:8080/sap/opu/odata/APLXCR/POS_MR_MAIN_SRV/MainSet?sap-client=300&$format=json&$select=Store,Businessdaydate,Originalsum,Adjustmentsum,Resultsum&$orderby=Store%2C%20Businessdaydate%20asc&$filter=IDateFrom%20eq%20%2720210101%27%20and%20IDateTo%20eq%20%2720250101%27")

    try:
        response = requests.get(url,auth = ('skrishnan','develop01'))
        print(f"----> Response {response.status_code}{response.reason}")
        if response.status_code == 200:
            sales = json.dumps(response.json(), indent=4)
            sales_json = json.loads(sales) # converts to dict

            data = sales_json

            #Access all the fields
            
            articles = data["d"]["results"]

            

            final_news = []

            #loop through all articles

            for article in articles:
                    source_name = article["Store"]
                    Businessdaydate = article["Businessdaydate"]
                    Originalsum = article["Originalsum"]
                    Adjustmentsum = article["Adjustmentsum"]
                    Resultsum = article["Resultsum"]
                    
                    title_description = f"""
                        Businessdaydate: {Businessdaydate},
                        Originalsum: {Originalsum},
                        Store: {source_name},
                        Adjustmentsum: {Adjustmentsum},
                        Resultsum: {Resultsum}
                     """
                    # outputObj = {
                    #     "Title": {title},
                    #     "Author": {author},
                    #     "Source": {source_name},
                    #     "Description": {description},
                    #     "URL": {url}  
                    # }
                    # results.append(outputObj)

                    final_news.append(title_description)
            return final_news
        else:
             return []

    except requests.exceptions.requests.RequestException as e:
        print("Error occured during API request",e)




class AssistantManager:
    thread_id = "thread_eErJA5m5bEe7ngL0R95ROwAz"
    assistant_id = "asst_udcFxDcIxx5Qph5ig1Cr1aoV"

    #constructor
    def __init__(self, model: str = model):
        self.client = client
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None

        # Retrieve existing assistant and thread if IDs are already set
        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=AssistantManager.assistant_id
            )
        
        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id=AssistantManager.thread_id
            )
        
    
    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=name, instructions=instructions, tools=tools, model=self.model
            )
            AssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"AssisID:::: {self.assistant.id}")
    
    def create_thread(self):
        if not self.thread:
            thread_obj = self.client.beta.threads.create()
            AssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"ThreadID::: {self.thread.id}")
    
    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id, role=role, content=content
            )
    
    def run_assistant(self, instructions):
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions,
            )

    def process_message(self):
        if self.thread:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            summary = []

            last_message = messages.data[0]
            role = last_message.role
            response = last_message.content[0].text.value
            summary.append(response)

            self.summary = "\n".join(summary)
            print(f"SUMMARY-----> {role.capitalize()}: ==> {response}")

            # for msg in messages:
            #     role = msg.role
            #     content = msg.content[0].text.value
            #     print(f"SUMMARY-----> {role.capitalize()}: ==> {content}")

    def wait_for_completion(self):
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id, run_id=self.run.id
                )
                print(f"RUN STATUS:: {run_status.model_dump_json(indent=4)}")

                if run_status.status == "completed":
                    self.process_message()
                    break
                elif run_status.status == "requires_action":
                    print("FUNCTION CALLING NOW...")
                    self.call_required_functions(
                        required_actions=run_status.required_action.submit_tool_outputs.model_dump()
                    )
    
    def call_required_functions(self, required_actions):
        if not self.run:
            return
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])

            if func_name == "get_sales":
                output = get_sales(topic=arguments["topic"])
                print(f"STUFFFFF;;;;{output}")
                final_str = ""
                for item in output:
                    final_str += "".join(item)

                tool_outputs.append({"tool_call_id": action["id"], "output": final_str})
            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Submitting outputs back to the Assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id, run_id=self.run.id, tool_outputs=tool_outputs
        )

    #for streamlit    
    def get_summary(self):
        return self.summary
    
    # Run the steps
    def run_steps(self):
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread.id, run_id=self.run.id
        )
        print(f"Run-Steps::: {run_steps}")
        return run_steps.data


def main():
   #news =   get_news("bitcon")
   #print(news[0])

   manager = AssistantManager()

   st.title("Sales Analyzer")

   with st.form(key="user_input_form"):
        instructions = st.text_input("Enter topic:")
        submit_button = st.form_submit_button(label="Run Assistant")
        
        if submit_button:
            manager.create_assistant(
                name="Sales Analyzer",
                instructions="You are a store sales analyzer who summarizers total sales for all stores",
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_sales",
                            "description": "Get the list of stores and summarize reveneue",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "topic": {
                                        "type": "string",
                                        "description": "The topic for the Store Analyzer, e.g. Sales for Store 0027",
                                    }
                                },
                                "required": ["topic"],
                            },
                        },
                    }
                ],
            )
            manager.create_thread()

            # Add the message and run the assistant
            manager.add_message_to_thread(
                role="user", content=f"Summarize Sales on this topic {instructions}?"
            )

            manager.run_assistant(instructions="Summarize Sales")

            # Wait for completions and process messages
            manager.wait_for_completion()

            summary = manager.get_summary()

            st.write(summary)

            st.text("Run Steps:")

            #Show run steps with line numbers
            st.code(manager.run_steps(), line_numbers=True)

            # # chart_data = pd.DataFrame(
            # #     {
            # #         "Title": np.random.randn(20),
            # #         "Author": np.random.randn(20),
            # #         "col3": np.random.choice(["Title", "Author", "C"], 20),
            # #     }
            # # )

            # st.area_chart(results, x="Title", y="Author", color="#ffaa00") 

if __name__ == "__main__":
    main()