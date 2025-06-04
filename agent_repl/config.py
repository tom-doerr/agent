import dspy
import os

def configure_dspy(model=None):
    model = model or os.getenv("DSPY_MODEL", "openrouter/deepseek/deepseek-chat-v3-0324")
    llm = dspy.LM(model=model)
    dspy.settings.configure(lm=llm)
    return llm
