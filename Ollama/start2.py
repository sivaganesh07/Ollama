from pyexpat.errors import messages
import ollama

response = ollama.list()

# print(response)

# res = ollama.chat( model="mistral",
#                    messages=[
#                        {
#                            "role": "user",
#                            "content": "How are you?"
#                        }
#                    ] )

# print(res["message"]["content"])

# res = ollama.chat( model="mistral",
#                     messages=[
#                         {
#                             "role": "user",
#                             "content": "How are you?"
#                         }
                        
#                     ],
#                     stream=True
#                     )

# for re in res:
#     print(re["message"]["content"], end="", flush=True)


# ==================================================================================
# ==== The Ollama Python library's API is designed around the Ollama REST API ====
# ==================================================================================

#== Generate example ==
# res = ollama.generate(
#     model="llama3.2",
#     prompt="How motor works?"
# )

#show
# print(res["response"])

# print(ollama.show("llama3.2"))


# Create a new model with modelfile
modelfile_path = """
FROM llama3.2
SYSTEM You are very smart assistant who knows everything about oceans. You are very succinct and informative.
PARAMETER temperature 0.1
"""

ollama.create(model='Siva', from_='llama3.2', system="You are Mario from Super Mario Bros.")

res = ollama.generate(model="Siva", prompt="Why is sea blue?")

print(res["response"])


# delete model
# ollama.delete("Siva")