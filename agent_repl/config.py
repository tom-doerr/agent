import dspy

def configure_dspy(model="openrouter/deepseek/deepseek-chat-v3-0324"):
    llm = dspy.LM(model=model)
    dspy.settings.configure(lm=llm)
    return llm
