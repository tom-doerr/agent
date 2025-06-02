import dspy

class NaturalLanguageToTaskwarrior(dspy.Signature):
    """Translates a natural language request about tasks into a Taskwarrior CLI command.
    The command should start with 'task'.
    Focus on interpreting dates, times, projects, tags, and priorities.
    For example, 'add a task to buy milk tomorrow evening' could become 'task add buy milk due:tomorrowT18:00'.
    'show me tasks for project home' could become 'task project:home list'.
    'what are my most urgent tasks' could become 'task priority:H list'.
    """
    user_request = dspy.InputField(desc="Natural language request related to task management.")
    taskwarrior_command = dspy.OutputField(desc="A valid Taskwarrior CLI command starting with 'task'.")

class TaskWarriorModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_command = dspy.ChainOfThought(NaturalLanguageToTaskwarrior)

    def forward(self, user_request):
        prediction = self.generate_command(user_request=user_request)
        return prediction
