from openai import OpenAI
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import mplcursors
load_dotenv()


client = OpenAI()

# # runs = client.beta.threads.runs.retrieve(
# #   thread_id="thread_eErJA5m5bEe7ngL0R95ROwAz",
# #   run_id="run_mIDuVoWoS104syS89BrvEWa3"
# # )

# # print(runs)




run = client.beta.threads.runs.cancel(
  thread_id="thread_eErJA5m5bEe7ngL0R95ROwAz",
  run_id="run_DB7Hd6CvlAbuIQZyNszfs1Yx"
)

print(run)


