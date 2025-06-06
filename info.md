# coding agent
the coding agent should be using deepseek-chat for now
please use the model openrouter/google/gemini-2.5-flash-preview-05-20
is able to search using firebase
the input text field should have vim key bindings
when i sent a request it should keep the focus on the input text field so don't have to refocus when i want to send the next message
i want to be able to interrupt responses. so when i send a new response while the old one is still processing i still want it to start working on the new message immediately
it should stream the tokens and the ui refresh shouldn't just happen all at once 






the project contains a memory gan
there's a value module which predicts socre and uncertainty 
there's a interface that let's me score the highest uncertainty items 
the items i manually scored get saved to train the value network
the rating interface lets me rate on a scale from 0 to 9

# dspy graph
i want a net/graph of dspy modules where each module is the same class but treated as seperate for optimization
i want each to be optimized seperately so we can have more custom prompts
each one determines the next module by outputing a number of the module that is ran next
we communicate the number of available modules
there needs to be a max number of steps which also gets communicated as part of the input
there should be a system context input that communicates num moduels and max number steps and the current step num
there are data and notes input and ouput fields that get passed between the modules
optimization happens with dspy simba
improvement gets logged to mlflow
