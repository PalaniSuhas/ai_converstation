from google import genai

# Replace with your actual API key
API_KEY = "AIzaSyD1kqpkXtl989bi2ML6QSoYluPAtOFMnQA"

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello and confirm the API is working."
)

print(response.text)
