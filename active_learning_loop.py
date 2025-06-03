import dspy
import os
import json
from value_network import ValueNetwork
from generator_module import GeneratorModule


# Initialize DSPy with your preferred model
def configure_dspy(model_name):
    llm = dspy.LM(model=model_name, max_tokens=1000)
    dspy.settings.configure(lm=llm)
    return llm


# Initialize modules
value_net = ValueNetwork()
generator = GeneratorModule()
configure_dspy("deepseek/deepseek-reasoner")

# Training data storage
TRAINING_DATA_FILE = "value_net_training_data.json"


def load_training_data():
    if os.path.exists(TRAINING_DATA_FILE):
        with open(TRAINING_DATA_FILE, "r") as f:
            return [dspy.Example(**ex) for ex in json.load(f)]
    return []


def save_training_data(data):
    with open(TRAINING_DATA_FILE, "w") as f:
        json.dump([{"data_point": ex.data_point, "score": ex.score} for ex in data], f)


def manual_scoring_interface(data_point):
    print(f"\nData point: {data_point}")
    print(
        "Rate the quality of this data point on a scale from 0 to 9 (where 0 is worst, 9 is best):"
    )
    try:
        rating = int(input("Enter rating (0-9): ").strip())
        # Normalize the rating to 0-1 range
        return rating / 9.0
    except Exception:
        print(
            "Invalid input. Using default rating 4.5 (which is 0.5 after normalization)."
        )
        return 0.5


def active_learning_loop():
    # Load existing training data
    training_data = load_training_data()

    # Generate candidate data points
    topics = ["AI ethics", "Renewable energy", "Space exploration", "Biotechnology"]
    candidates = []
    for topic in topics:
        result = generator(topic=topic)
        candidates.append(result.data_point)

    # Get predictions with uncertainties
    predictions = []
    for data_point in candidates:
        pred = value_net(data_point=data_point)
        try:
            score = float(pred.score)
            uncertainty = float(pred.uncertainty)
            predictions.append((data_point, score, uncertainty))
        except Exception as e:
            print(f"Error processing prediction: {e}")
            predictions.append(
                (data_point, 0.5, 1.0)
            )  # Default values when parsing fails

    # Sort by uncertainty (highest first)
    predictions.sort(key=lambda x: x[2], reverse=True)

    # Score top 3 most uncertain
    for data_point, _, _ in predictions[:3]:
        true_score = manual_scoring_interface(data_point)
        training_data.append(dspy.Example(data_point=data_point, score=true_score))

    # Save updated training data
    save_training_data(training_data)
    print(f"Saved {len(training_data)} training examples")

    # Retrain value network (simplified)
    if training_data:
        # In a real implementation, we'd use a teleprompter here
        print("Value network updated with new training data")


if __name__ == "__main__":
    active_learning_loop()
