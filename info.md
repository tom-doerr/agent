# dspy rl
there should be a reward function that i can call at any point and assign reward that gets applied, discounted, to all previous steps to a episode
should have some way of marking the end or beginning of a new episode
should provide a cli tool that restarts the program up to max number of times, applying a negative reward every time the program crashes, fails and applying a positive reward if it exits succesfully
the reward should be used to determine which few-shot examples to use for dspy modules
every inference, input output pair, should be a candidate for a few-shot example
maybe use bayesian optimization for picking few-shot examples to try
we should use multiple few-shot examples for each inference so we can gather more data
i think it should be possible for bayesian optimization to result in no few-shot examples so we make it possible for the agent to figure things out and not be misguided by previous attempts if no attempt succeeded yet
this dspy rl system should be a module itself so i can easily use it in dspy workflows
it should automatically load the best few-shot examples for normal inferenceit 
should be possible to keep optimizing few-shot examlples during normal execution





# simpledspy agent
i would want to later have it ran many operations in parallel, like consolidating memory, reflecting, research, while messaging the user and looking for releveant information to load into short term memory 
i would like to have a fast model and a slower reasoning model like deepseek r1 for reasoning

# reasoning
i would want to somehow make use of the deepseek r1 reasoning model. how could we use dspy to make better use of the reaosning models? i was thinking that maybe we could provide a list with constraints and give them to a dspy module and let it edit whichever system it is working on using filename search replace blocks. could be a book, a program, presentation, paper. we then task a reasoning model to compare the original version with the edited version and assign a rating on a scale from 1 to 10 for each constraint for each version. we then keep the version if the overall score has improved. note though that we somehow we should give higher weight to dimensions/constraints with low score, so we might want to just use l2 loss and square the distance to a perfect 10 score for each constraint and add them up. the delta in loss change could then be use during optimization of the dspy module



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
