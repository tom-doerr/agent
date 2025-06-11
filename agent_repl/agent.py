import dspy

class CodingAgentSignature(dspy.Signature):
    """Execute coding tasks autonomously. You can search Firebase by using 'firebase:' prefix in commands."""
    request = dspy.InputField(desc="User request for code changes")
    log_context = dspy.InputField(desc="Relevant log entries for context")
    plan = dspy.OutputField(desc="Step-by-step plan to complete request")
    commands = dspy.OutputField(desc="Shell commands to execute. Use 'firebase:query' for Firebase searches.")
    edits = dspy.OutputField(desc="File edits in SEARCH/REPLACE block format")
    done = dspy.OutputField(desc="'DONE' when task is complete, 'CONTINUE' to process next step autonomously")
    uncertainty = dspy.OutputField(desc="Confidence score between 0.0 and 1.0, 1.0 being most confident")

class CodingAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.agent = dspy.ChainOfThought(CodingAgentSignature)
    
    def forward(self, request, log_context):
        return self.agent(request=request, log_context=log_context)
