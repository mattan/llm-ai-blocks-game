import requests
import json
import toml

# Read API key from secret.toml
with open("secret.toml", "r", encoding="utf-8") as f:
    secrets = toml.load(f)
    api_key = secrets["AZURE_OPENAI_API_KEY"]

# Azure OpenAI resource base URL (without deployment)
BASE_URL = "https://niv94-mbg3mu33-eastus2.cognitiveservices.azure.com/openai/deployments"
API_VERSION = "2025-01-01-preview"

def log_interaction(deployment_name: str, question: str, answer: str):
    with open("token_manager/gpt_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"Deployment: {deployment_name}\nQuestion: {question}\nAnswer: {answer}\n{'-'*40}\n")

def ask_gpt(question: str, deployment_name: str = "gpt-4o") -> str:
    """
    Sends a question to the Azure OpenAI API (deployment is dynamic) and returns the response.
    """
    endpoint = f"{BASE_URL}/{deployment_name}/chat/completions?api-version={API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    data = {
        "messages": [
            {"role": "user", "content": question}
        ],
        "max_tokens": 512,
        "temperature": 0.7
    }
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        log_interaction(deployment_name, question, answer)
        return answer
    else:
        error_msg = f"Error: {response.status_code} - {response.text}"
        log_interaction(deployment_name, question, error_msg)
        return error_msg

if __name__ == "__main__":
    question = "מה בירת ישראל?"
    print("שולח שאלה ל-GPT-4o...")
    answer = ask_gpt(question)
    print("תשובה:", answer)
