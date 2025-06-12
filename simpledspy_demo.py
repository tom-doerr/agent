#!/usr/bin/env python3


from simpledspy import predict


input_message = 'hi there'
message_to_user = predict(input_message)
print(f'message to user: {message_to_user}')


