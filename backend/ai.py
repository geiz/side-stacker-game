from llama_cpp import Llama
import os

# Path to your GGUF model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "mistral-7b-instruct-v0.2-code-ft.Q3_K_M.gguf")

# Load the model
llm = Llama(model_path=MODEL_PATH, n_ctx=512, n_threads=4, n_gpu_layers=20)  # Adjust context size & threads as needed

def generate_response(prompt):
    response = llm(
        prompt,
        max_tokens=256,
        temperature=0.7,
        top_p=0.9
    )
    return response["choices"][0]["text"].strip()

# Test it
if __name__ == "__main__":
    print(generate_response("Say Hello! Nothing else."))
