#!/usr/bin/env python3

from simpledspy import predict

a = 'jkl'
b = 'abc'

# a_reversed, b_repeated = predict(b, a)
a_reversed, b_repeated = predict(b, a, description='reverse a and repeat b')
print(f'a_reversed: {a_reversed}')
print(f'b_repeated: {b_repeated}')

