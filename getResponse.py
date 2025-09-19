from ollama import chat, ChatResponse

def generate_response(input_text: str) -> str:
    # Generate the response using the Ollama Python client
    response: ChatResponse = chat(
        model="mistral",  # or "llama3.2", "llama3.3", "deepseek-r1:14b"
        messages=[{"role": "user", "content": input_text}],
    )

    # Extract and return the response content
    return response.message.content

if __name__ == "__main__":
    print(generate_response("Hi model, how is the weather?"))
