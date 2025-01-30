
from altair import Description
import openai
import os
import requests
import json
import time
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



load_dotenv()

# Load library and model
client = openai.OpenAI()
model = "gpt-4.0-mini"

# Load news api
news_api_key = os.environ.get("NEWS_API_KEY")

results = []    

def generate_code(topic,inputjson):
        print(f"----> generate code {topic} {inputjson}")

        full_prompt = f"""
        I have the following data:
        {inputjson}

        User prompt: "{topic}"

        Generate raw Python code to create a bar chart based on the user's prompt using matplotlib,streamlit and use `ax.bar_label(bars, fmt="%.2f", padding=3)` to show data labels to bars.Output only valid Python code without Markdown formatting like triple backticks
        
        """

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Python programming assistant which only prints raw python code output (without Markdown formatting like triple backticks)"},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
        )

        # Extract generated Python code
        generated_code = response.choices[0].message.content

        print(f"------> Code Genereated : {generated_code} ")
        return generated_code

def get_sales(topic):
    print(f"----> LOG {topic}")
    url = (f"https://s4crm.applexus.com:8888/sap/opu/odata/APLXCR/POS_MR_MAIN_SRV/MainSet?sap-client=300&$format=json&$top=50&$select=Store,Businessdaydate,Originalsum,Adjustmentsum,Resultsum&$orderby=Store%2C%20Businessdaydate%20asc&$filter=IDateFrom%20eq%20%2720220101%27%20and%20IDateTo%20eq%20%2720220201%27")

    try:
        response = requests.get(url,auth = (os.getenv("USER_ID"),os.getenv("PASSWORD")))
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
                        Businessdaydate: {Businessdaydate[:4]},
                        Originalsum: {Originalsum},
                        Store: {source_name.lstrip('0') },
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

    except requests.exceptions as e:
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
        self.code = None
        self.jsoninput = None

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

            # print(f" Before summary print {messages}")

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

                self.jsoninput = final_str
                tool_outputs.append({"tool_call_id": action["id"], "output": final_str})
            
            elif func_name == "generate_code":
                chartoutput = generate_code(topic=arguments["topic"],inputjson=self.jsoninput)
                self.code = chartoutput
                tool_outputs.append({"tool_call_id": action["id"], "output": chartoutput})
                

            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Submitting outputs back to the Assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id, run_id=self.run.id, tool_outputs=tool_outputs
        )

    #for streamlit    
    def get_summary(self):
        return self.summary
    
    #for get code
    def get_code(self):
        return self.code
    
    # Run the steps
    def run_steps(self):
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread.id, run_id=self.run.id
        )
        print(f"Run-Steps::: {run_steps}")
        return run_steps.data    
    

    def generate_chart(self,code):
        print(f"----> generate chart {code}")

        # Set up a local namespace for execution
        local_namespace = {"st": st, "plt": plt, "pd": pd}        
        
        # Executes the Python code generated by OpenAI.
    
        try:
            exec(code, globals(),local_namespace)
        except Exception as e:
            print("Error executing the generated code:", e)


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
                instructions="You are an assistant that only performs Sales analysis using the get_sales function to get sales data",
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
                        }

                                            
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "generate_code",
                            "description": "You are an assistant who generates python code to generate charts using Streamlit,matplotlib.Output only valid Python code without Markdown formatting like triple backticks",                        
                            "parameters": {
                                "type": "object",
                                "properties": {
                                "topic": {
                                    "type": "string",
                                    "description": "User prompt given to generate chats. e.g. Give me chart for sales in 2022 and 2021"
                                }
                                },                            
                                "required": [
                                "topic"
                                ]
                            }

                        }
                    }
                    
                ],
                
            )
            manager.create_thread()

            # Add the message and run the assistant
            manager.add_message_to_thread(
                role="user", content=f"{instructions}?"
            )

            manager.run_assistant(instructions="Your task is to perform sales analysis. Start by calling the `get_sales` function to obtain sales data. If a user requests a chart, call the `generate_code` function to build the chart.")

            # Wait for completions and process messages
            manager.wait_for_completion()

            summary = manager.get_summary()

            code = manager.get_code()

            

            

            st.text("Run Steps:")

            # Execute the generated code
            if code:
                st.subheader("Generated Python Code:")
                st.code(code, language="python")
                st.subheader("Generated Chart:")
                manager.generate_chart(code)
            else:
                st.write(summary)
            

            #Show run steps with line numbers
            st.code(manager.run_steps(), line_numbers=True)
            manager.code = ''

            

if __name__ == "__main__":
    main()