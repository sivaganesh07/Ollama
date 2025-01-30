import vertexai


vertexai.init(project='My First Project', location='us-central1')

from vertexai.generative_models import GenerativeModel  # noqa: E402
model = GenerativeModel("gemini-pro")
print(model.generate_content("Why is sky blue?"))