#!/usr/bin/env python3

from simpledspy import predict
import dspy

# dspy.configure(lm=dspy.LM('openrouter/google/gemini-2.5-flash-preview', cache=False, max_tokens=10000))
# dspy.configure(lm=dspy.LM('deepseek/deepseek-chat'))
dspy.configure(lm=dspy.LM('deepseek/deepseek-reasoner', cache=False, max_tokens=10000))


a = 'jkl'
b = 'abc'
c = 'xyz'

a_reversed, b_repeated, a_plus_b, c_plus_a = predict(b, a, c)
print(f'a_reversed: {a_reversed}'); print(f'b_repeated: {b_repeated}'); print(f'a_plus_b: {a_plus_b}'); print(f'c_plus_a: {c_plus_a}')

a_reversed, b_repeated, a_plus_b = predict(b, a)
print(f'a_reversed: {a_reversed}'); print(f'b_repeated: {b_repeated}'); print(f'a_plus_b: {a_plus_b}')


# a_reversed, b_repeated = predict(b, a)
# a_reversed, b_repeated = predict(b, a, description='reverse a and repeat b')
a_reversed, b_repeated = predict(b, a)
print(f'a_reversed: {a_reversed}'); print(f'b_repeated: {b_repeated}')

# a_reversed, b_repeated = predict(a, b, description='reverse a and repeat b')
a_reversed, b_repeated = predict(a, b)
print(f'a_reversed: {a_reversed}'); print(f'b_repeated: {b_repeated}')

# b_reversed, a_repeated = predict(a, b, description='reverse a and repeat b')
b_reversed, a_repeated = predict(a, b)
print(f'a_reversed: {a_reversed}'); print(f'b_repeated: {b_repeated}')
