# from openai import OpenAI
# from dotenv import load_dotenv
# import matplotlib.pyplot as plt
# import mplcursors
# load_dotenv()


# client = OpenAI()

# # runs = client.beta.threads.runs.retrieve(
# #   thread_id="thread_eErJA5m5bEe7ngL0R95ROwAz",
# #   run_id="run_mIDuVoWoS104syS89BrvEWa3"
# # )

# # print(runs)




# run = client.beta.threads.runs.cancel(
#   thread_id="thread_eErJA5m5bEe7ngL0R95ROwAz",
#   run_id="run_XB8whaikKLroSAOUIx6uEgID"
# )

# print(run)

import matplotlib.pyplot as plt
import streamlit as st

# Data
data = [
    {"Businessdaydate": 2022, "Originalsum": 156.040, "Store": 24, "Adjustmentsum": 43.450, "Resultsum": 112.590},
    {"Businessdaydate": 2022, "Originalsum": 578.000, "Store": 100, "Adjustmentsum": 244.480, "Resultsum": 333.520},
    {"Businessdaydate": 2022, "Originalsum": 156.040, "Store": 24, "Adjustmentsum": 43.450, "Resultsum": 112.590},
    {"Businessdaydate": 2022, "Originalsum": 578.000, "Store": 100, "Adjustmentsum": 244.480, "Resultsum": 333.520}
]

stores = [d['Store'] for d in data]
resultsum = [d['Resultsum'] for d in data]

# Create Plot
fig, ax = plt.subplots()

bars = ax.bar(stores, resultsum)

# Adding data labels to bars
ax.bar_label(bars, fmt="%.2f", padding=3)

# Set plot title
plt.title("Sales Chart for 2022")

# Display plot in Streamlit
st.pyplot(fig)


