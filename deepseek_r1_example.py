import dspy
import os

# 1. Configure DSPy to use DeepSeek directly via its OpenAI-compatible API
# Ensure your DEEPSEEK_API_KEY environment variable is set.
# DSPy, through LiteLLM, should pick up the API key automatically.
model_to_use = "deepseek/deepseek-reasoner"
llm = dspy.LM(
    model=model_to_use,
    # api_key=os.getenv("DEEPSEEK_API_KEY") # LiteLLM picks this up from env
)
dspy.settings.configure(lm=llm)

# 2. Define a simple signature for question answering
class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often a short phrase or a few words")

# 3. Create a dspy.Predict module
predict_answer = dspy.Predict(BasicQA)

# 4. Ask a question
question_to_ask = "What is the capital of France?"

print(f"\nAsking '{question_to_ask}' using dspy.LM configured for DeepSeek model '{model_to_use}'\n")

try:
    # 5. Get the prediction
    response = predict_answer(question=question_to_ask)

    # 6. Print the answer
    print(f"Question: {question_to_ask}")
    print(f"Answer: {response.answer}")

except Exception as e:
    print(f"An error occurred: {e}")

# To run this script:
# 1. Ensure 'dspy-ai' and 'python-dotenv' are in your requirements.txt and installed.
# 2. Set your DEEPSEEK_API_KEY environment variable.
# 3. Execute: .venv/bin/python /home/tom/git/agent/deepseek_r1_example.py (or activate venv first)

