import dspy
import os
import json
from dspy_programs.value_network import ValueNetwork, optimize_value_network
from dspy_programs.generator_module import GeneratorModule, optimize_generator

# Training data storage
TRAINING_DATA_FILE = "value_net_training_data.json"

def configure_dspy(model_name="deepseek/deepseek-chat"):
    llm = dspy.LM(
        model=model_name,
        max_tokens=1000
    )
    dspy.settings.configure(lm=llm)
    return llm

def load_training_data():
    if os.path.exists(TRAINING_DATA_FILE):
        try:
            with open(TRAINING_DATA_FILE, 'r') as f:
                data = json.load(f)
                return [dspy.Example(data_point=ex['data_point'], score=ex['score']) for ex in data]
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {TRAINING_DATA_FILE}")
            return []
    return []

def save_training_data(data):
    with open(TRAINING_DATA_FILE, 'w') as f:
        json.dump([{'data_point': ex.data_point, 'score': ex.score} for ex in data], f)

def manual_scoring_interface(data_point):
    print(f"\nData point: {data_point}")
    while True:
        try:
            rating_str = input("Rate the quality of this data point (0-9 where 0=worst, 9=best): ").strip()
            if not rating_str:
                raise ValueError("Empty input")
                
            rating = int(rating_str)
            if rating < 0 or rating > 9:
                print("Please enter a number between 0 and 9.")
                continue
                
            return rating / 9.0
        except ValueError:
            print("Invalid input. Please enter a number between 0 and 9.")

def active_learning_loop():
    # Configure DSPy
    configure_dspy()
    
    # Initialize modules
    value_net = ValueNetwork()
    generator = GeneratorModule()
    
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
            predictions.append((data_point, 0.5, 1.0))
    
    # Sort by uncertainty (highest first)
    predictions.sort(key=lambda x: x[2], reverse=True)
    
    print("\nCandidates sorted by uncertainty:")
    for i, (data_point, score, uncertainty) in enumerate(predictions):
        print(f"{i+1}. Uncertainty: {uncertainty:.2f}, Score: {score:.2f}")
        print(f"   Data: {data_point[:100]}...")
    
    # Score top 3 most uncertain
    for data_point, _, _ in predictions[:3]:
        true_score = manual_scoring_interface(data_point)
        training_data.append(dspy.Example(
            data_point=data_point,
            score=true_score
        ))
    
    # Save updated training data
    save_training_data(training_data)
    print(f"\nSaved {len(training_data)} training examples")
    
    # Retrain value network
    if training_data:
        print("Optimizing value network with new training data")
        value_net = optimize_value_network(training_data)
        print("Optimizing generator with new training data")
        generator = optimize_generator(training_data)

if __name__ == "__main__":
    active_learning_loop()
