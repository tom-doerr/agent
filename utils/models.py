"""Common model building and management patterns for DSPy models."""

import time
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, Union
import dspy

T = TypeVar('T')


class ModelManager:
    """Base class for managing DSPy models with versioning and caching."""
    
    def __init__(self, model_dir: str = "models", model_prefix: str = "model"):
        self.model_dir = Path(model_dir)
        self.model_prefix = model_prefix
        self.model_dir.mkdir(exist_ok=True)
    
    def get_latest_path(self) -> Path:
        """Get path to latest model symlink."""
        return self.model_dir / f"{self.model_prefix}_latest.pkl"
    
    def get_versioned_path(self, timestamp: Optional[int] = None) -> Path:
        """Get path for a versioned model."""
        if timestamp is None:
            timestamp = int(time.time())
        return self.model_dir / f"{self.model_prefix}_{timestamp}.pkl"
    
    def save_with_versioning(self, model: Any) -> Path:
        """Save model with timestamp versioning and update latest symlink."""
        versioned_path = self.get_versioned_path()
        latest_path = self.get_latest_path()
        
        # Save versioned model
        model.save(str(versioned_path))
        
        # Update symlink to latest
        if latest_path.exists() or latest_path.is_symlink():
            latest_path.unlink()
        latest_path.symlink_to(versioned_path.name)
        
        return versioned_path
    
    def load_latest(self, model_class: type) -> Optional[Any]:
        """Load the latest saved model if it exists."""
        latest_path = self.get_latest_path()
        if latest_path.exists():
            try:
                return model_class.load(str(latest_path))
            except Exception:
                return None
        return None


def build_or_load_model(
    model_class: type,
    builder_fn: Callable[[], T],
    model_manager: ModelManager,
    force_rebuild: bool = False
) -> T:
    """
    Generic pattern for building or loading a DSPy model.
    
    Args:
        model_class: The DSPy model class
        builder_fn: Function that builds and trains the model
        model_manager: ModelManager instance for saving/loading
        force_rebuild: If True, always rebuild the model
    
    Returns:
        The loaded or newly built model
    """
    if not force_rebuild:
        model = model_manager.load_latest(model_class)
        if model is not None:
            return model
    
    # Build new model
    model = builder_fn()
    
    # Save with versioning
    model_manager.save_with_versioning(model)
    
    return model


def create_training_examples(
    data: list,
    example_builder_fn: Callable[[Any], dspy.Example],
    shuffle: bool = True
) -> list:
    """
    Create training examples from data with a builder function.
    
    Args:
        data: Raw training data
        example_builder_fn: Function to convert data item to dspy.Example
        shuffle: Whether to shuffle the examples
    
    Returns:
        List of dspy.Example objects
    """
    import random
    
    examples = [example_builder_fn(item) for item in data]
    
    if shuffle:
        random.shuffle(examples)
    
    return examples


def optimize_with_bootstrap(
    model: dspy.Module,
    train_examples: list,
    val_examples: Optional[list] = None,
    metric: Optional[Callable] = None,
    **optimizer_kwargs
) -> dspy.Module:
    """
    Optimize a model using BootstrapFewShotWithRandomSearch.
    
    Args:
        model: The DSPy model to optimize
        train_examples: Training examples
        val_examples: Validation examples (uses subset of train if None)
        metric: Evaluation metric (uses simple equality if None)
        **optimizer_kwargs: Additional arguments for the optimizer
    
    Returns:
        Optimized model
    """
    if val_examples is None:
        val_examples = train_examples[:20]  # Use first 20 for validation
    
    if metric is None:
        # Default metric for classification tasks
        def metric(ex, pred, trace=None):
            # Assumes the example has a field that matches the prediction
            for field in pred.keys():
                if hasattr(ex, field):
                    return str(pred[field]) == str(getattr(ex, field))
            return False
    
    # Default optimizer settings
    default_kwargs = {
        "max_bootstrapped_demos": 4,
        "num_candidate_programs": 10,
        "num_threads": 4
    }
    default_kwargs.update(optimizer_kwargs)
    
    optimizer = dspy.BootstrapFewShotWithRandomSearch(
        metric=metric,
        **default_kwargs
    )
    
    return optimizer.compile(
        model,
        trainset=train_examples,
        valset=val_examples
    )


# Common DSPy signatures that can be reused
class RankingSignature(dspy.Signature):
    """Common signature for pairwise ranking tasks."""
    item_a: str = dspy.InputField(desc="First item to compare")
    item_b: str = dspy.InputField(desc="Second item to compare")
    better: str = dspy.OutputField(desc="Which item is better: 'A' or 'B'")
    reasoning: str = dspy.OutputField(desc="Explanation for the choice")


class ClassificationSignature(dspy.Signature):
    """Common signature for classification tasks."""
    text: str = dspy.InputField(desc="Text to classify")
    label: str = dspy.OutputField(desc="Classification label")
    confidence: float = dspy.OutputField(desc="Confidence score (0-1)")


class JudgmentSignature(dspy.Signature):
    """Common signature for judgment/evaluation tasks."""
    text: str = dspy.InputField(desc="Text to evaluate")
    helpful: bool = dspy.OutputField(desc="Whether the text is helpful/useful")
    explanation: str = dspy.OutputField(desc="Explanation for the judgment")
    score: float = dspy.OutputField(desc="Numeric score (0-1)")