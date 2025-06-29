#!/usr/bin/env python3

import dspy, reasoning_gym, sys
dspy_version_installed = dspy.__version__
print(dspy_version_installed)

# 1️⃣  Wire DeepSeek-R1 7B served by Ollama
# lm = dspy.LM( 'ollama/deepseek-r1:7b', api_base='http://localhost:11434', api_key='')
# lm = dspy.LM('openrouter/google/gemini-2.5-flash-lite-preview-06-17')
# lm = dspy.LM('openrouter/deepseek/deepseek-r1-0528-qwen3-8b', max_tokens=20000)
# lm = dspy.LM('openrouter/deepseek/dnereek-r1-0528', max_tokens=20000, temperature=1.5)
lm = dspy.LM('deepseek/deepseek-reasoner', max_tokens=20000, temperature=1.5)
# dspy.configure(lm=lm, parallel=False)   # single-thread to avoid OOM on CPU
dspy.configure(lm=lm, parallel=True)   # single-thread to avoid OOM on CPU

# 2️⃣  Tiny training batch from Reasoning Gym (“leg_counting” task)
# train_ds = reasoning_gym.create_dataset('leg_counting', size=40, seed=0)
train_ds = reasoning_gym.create_dataset('figlet_font', size=40, seed=0)
trainset = [
    dspy.Example(question=e["question"], answer=str(e["answer"]))
        .with_inputs("question")
    for e in train_ds
]

qa = dspy.Predict("question -> answer")
# qa = dspy.ChainOfThought('question -> answer')

# 4️⃣  Exact-match metric
def em(ex, pred, trace=None):
    return float(pred.answer.strip() == ex.answer.strip())

# 5️⃣  Prompt-optimize with SIMBA (stochastic mini-batch ascent)
# simba = dspy.SIMBA(metric=em, bsize=6, max_steps=4, max_demos=3)

simba = dspy.SIMBA(metric=em, num_threads=100)
better_qa = simba.compile(qa, trainset=trainset, seed=42)

# 6️⃣  Quick smoke-test
test = reasoning_gym.create_dataset('leg_counting', size=1, seed=1337)[0]
print("Q:", test["question"])
print("A:", better_qa(question=test["question"]).answer)





























































