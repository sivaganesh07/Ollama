import ollama
import os
import pandas as pd

model = "mistral"

input_file = "./data/Testcsv.csv"
output_file = "./data/OverallTransaction.txt"

# Check if the input file exists
if not os.path.exists(input_file):
    print(f"Input file '{input_file}' not found.")
    exit(1)

df = pd.read_csv(input_file)

json_data = df.iloc[1:].to_json(orient='records') 

print(json_data)

# Prepare the prompt for the model
prompt = f"""
JSON data: {df}

**1. Process the JSON data:**

   * Extract the "STORE" and the year from the "TRANSACTION_DATE" (e.g., "2023") from each object.

**2. Group the data:** 

   * Group the data by "STORE" and the extracted year.

**3. Calculate the sum of "AMOUNT"** 

   * For each unique combination of "STORE" and year, calculate the sum of the "AMOUNT" values.

**4. Present the results:** 

   * Output the results in a clear and concise format, for example:

      * Store: 1008.0, Year: 2023, Total Amount: 87358.0
      * Store: 1008.0, Year: 2024, Total Amount: 50.0 
"""   

# Send the prompt and get the response
try:
    response = ollama.generate(model=model, prompt=prompt)
    generated_text = response.get("response", "")
    print("==== Sales List: ===== \n")
    print(generated_text)

    # Write the categorized list to the output file
    with open(output_file, "w") as f:
        f.write(generated_text.strip())

    print(f"Sales list has been saved to '{output_file}'.")
except Exception as e:
    print("An error occurred:", str(e))