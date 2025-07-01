#!/usr/bin/env python3
"""
Compare simulated vs real Qwen3 embeddings for text ranking.
"""

import numpy as np
from qwen3_embedding_value_learner import Qwen3EmbeddingValueLearner, RankingExample
from qwen3_embedding_real import Qwen3RealEmbeddingLearner, SENTENCE_TRANSFORMERS_AVAILABLE, TRANSFORMERS_AVAILABLE


def compare_embeddings():
    """Compare simulated and real Qwen3 embeddings."""
    print("Qwen3 Embeddings Comparison: Simulated vs Real")
    print("=" * 60)
    
    # Training data
    training_examples = [
        RankingExample("Outstanding quality! Best purchase ever made. Highly recommend to everyone.", 9.8),
        RankingExample("Excellent product with great features. Very satisfied with the purchase.", 9.0),
        RankingExample("Good quality for the price. Some minor issues but overall happy.", 7.5),
        RankingExample("Decent product. Works as expected but nothing special.", 6.0),
        RankingExample("Average at best. There are better options available.", 5.0),
        RankingExample("Below average quality. Not worth the price.", 3.5),
        RankingExample("Poor product. Many problems and issues.", 2.5),
        RankingExample("Terrible quality. Broke immediately. Avoid!", 1.0),
    ]
    
    # Test texts
    test_texts = [
        "Amazing product! Exceeded all expectations!",
        "This is absolute garbage. Total waste of money.",
        "It's okay. Does what it's supposed to do.",
        "Best thing I've ever bought! Life changing!",
        "Completely broken. Doesn't work at all.",
    ]
    
    # 1. Simulated Embeddings
    print("\n1. SIMULATED EMBEDDINGS (Original Implementation)")
    print("-" * 60)
    
    sim_learner = Qwen3EmbeddingValueLearner(
        embedding_dim=128,
        ridge_alpha=1.0
    )
    
    sim_learner.add_training_examples(training_examples)
    sim_metrics = sim_learner.train(validation_split=0.25)
    
    print(f"Validation R²: {sim_metrics['val_r2']:.3f}")
    print(f"CV MSE: {sim_metrics['cv_mse_mean']:.3f} ± {sim_metrics['cv_mse_std']:.3f}")
    
    print("\nRankings with simulated embeddings:")
    sim_rankings = sim_learner.rank_texts(test_texts)
    for i, (text, score) in enumerate(sim_rankings, 1):
        print(f"{i}. Score: {score:6.2f} | {text[:50]}...")
    
    # 2. Real Embeddings (if available)
    if SENTENCE_TRANSFORMERS_AVAILABLE or TRANSFORMERS_AVAILABLE:
        print("\n\n2. REAL QWEN3 EMBEDDINGS")
        print("-" * 60)
        
        try:
            real_learner = Qwen3RealEmbeddingLearner(
                model_name="Qwen/Qwen3-Embedding-0.6B",
                ridge_alpha=1.0,
                use_sentence_transformers=SENTENCE_TRANSFORMERS_AVAILABLE,
                task_description="Rank product reviews by quality and sentiment"
            )
            
            real_learner.add_training_examples(training_examples)
            real_metrics = real_learner.train(validation_split=0.25)
            
            print(f"Validation R²: {real_metrics['val_r2']:.3f}")
            print(f"CV MSE: {real_metrics['cv_mse_mean']:.3f} ± {real_metrics['cv_mse_std']:.3f}")
            
            print("\nRankings with real Qwen3 embeddings:")
            real_rankings = real_learner.rank_texts(test_texts)
            for i, (text, score) in enumerate(real_rankings, 1):
                print(f"{i}. Score: {score:6.2f} | {text[:50]}...")
            
            # Compare similarity scores
            print("\n\n3. SEMANTIC SIMILARITY COMPARISON")
            print("-" * 60)
            
            test_pairs = [
                ("Great product!", "Excellent item!"),
                ("Great product!", "Terrible product!"),
                ("I love this", "I hate this"),
                ("Fast shipping", "Quick delivery"),
                ("High quality", "Low quality"),
            ]
            
            print("Text Pair                                          | Simulated | Real")
            print("-" * 70)
            
            for text1, text2 in test_pairs:
                # Simulated similarity
                emb1_sim = sim_learner._get_embedding_vector(text1)
                emb2_sim = sim_learner._get_embedding_vector(text2)
                sim_similarity = np.dot(emb1_sim, emb2_sim)
                
                # Real similarity
                real_similarity = real_learner.compute_similarity(text1, text2)
                
                pair_str = f"{text1} <-> {text2}"
                print(f"{pair_str:50} | {sim_similarity:9.3f} | {real_similarity:9.3f}")
            
            # Performance comparison
            print("\n\n4. PERFORMANCE COMPARISON")
            print("-" * 60)
            print(f"Metric                  | Simulated    | Real")
            print("-" * 45)
            print(f"Validation R²          | {sim_metrics['val_r2']:11.3f} | {real_metrics['val_r2']:11.3f}")
            print(f"Validation MSE         | {sim_metrics['val_mse']:11.3f} | {real_metrics['val_mse']:11.3f}")
            print(f"CV MSE Mean           | {sim_metrics['cv_mse_mean']:11.3f} | {real_metrics['cv_mse_mean']:11.3f}")
            print(f"Embedding Dimension    | {sim_learner.embedding_dim:11d} | {real_learner.embedding_dim:11d}")
            
        except Exception as e:
            print(f"Error loading real Qwen3 model: {e}")
            print("\nThis might be due to:")
            print("1. Model not downloaded yet (first run takes time)")
            print("2. Insufficient memory (try a smaller model)")
            print("3. Missing dependencies")
    
    else:
        print("\n\nREAL EMBEDDINGS NOT AVAILABLE")
        print("-" * 60)
        print("To use real Qwen3 embeddings, install:")
        print("  pip install sentence-transformers")
        print("  # or")
        print("  pip install transformers torch")
    
    print("\n\n5. KEY DIFFERENCES")
    print("-" * 60)
    print("Simulated Embeddings:")
    print("- Based on surface features (length, punctuation, keywords)")
    print("- Fast and lightweight")
    print("- No semantic understanding")
    print("- Good for testing and development")
    print()
    print("Real Qwen3 Embeddings:")
    print("- True semantic understanding")
    print("- Captures meaning and context")
    print("- Multilingual support (100+ languages)")
    print("- State-of-the-art performance")
    print("- Requires GPU for best performance")


if __name__ == "__main__":
    compare_embeddings()