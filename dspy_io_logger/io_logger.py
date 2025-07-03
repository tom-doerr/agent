import dspy
import json
import os
from typing import Any, Dict

class IOLogger(dspy.Module):
    def __init__(self, module: dspy.Module, log_file: str = "io_log.jsonl"):
        super().__init__()
        self.module = module
        self.log_file = log_file
        # Ensure directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    def forward(self, **kwargs: Dict[str, Any]) -> Any:
        output = self.module(**kwargs)
        with open(self.log_file, "a") as f:
            log_entry = {"input": kwargs, "output": output}
            f.write(json.dumps(log_entry) + "\n")
        return output
