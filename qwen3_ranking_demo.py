#!/usr/bin/env python3
"""
Demo script showing practical usage of Qwen3 Embedding Value Learner.
"""

import os
from qwen3_embedding_value_learner import Qwen3EmbeddingValueLearner, RankingExample


def product_review_ranking_demo():
    """Demo: Ranking product reviews by quality/helpfulness."""
    print("=== Product Review Ranking Demo ===\n")
    
    # Initialize learner
    learner = Qwen3EmbeddingValueLearner(
        embedding_dim=256,  # Moderate size for reviews
        ridge_alpha=10.0,   # Higher regularization for noisy data
        api_key=os.environ.get("OPENROUTER_API_KEY")  # Optional
    )
    
    # Training data: Reviews with helpfulness scores (0-10)
    training_reviews = [
        # High-quality reviews
        RankingExample(
            "After using this product for 3 months, I can confidently say it's worth every penny. "
            "The build quality is exceptional, and it performs exactly as advertised. "
            "The customer service was also responsive when I had questions.",
            score=9.5
        ),
        RankingExample(
            "Pros: Durable construction, easy to use, great value. "
            "Cons: Slightly heavier than expected. "
            "Overall, I'm very satisfied and would recommend to others.",
            score=8.5
        ),
        
        # Medium-quality reviews
        RankingExample(
            "Good product. Works fine. No major complaints.",
            score=5.0
        ),
        RankingExample(
            "It's okay. Does what it's supposed to do but nothing special.",
            score=4.5
        ),
        
        # Low-quality reviews
        RankingExample(
            "Bad!!!",
            score=1.0
        ),
        RankingExample(
            "Waste of money",
            score=1.5
        ),
        RankingExample(
            "arrived broken. returning it.",
            score=2.0
        ),
        
        # More examples for better training
        RankingExample(
            "I've tested this against 3 competitor products and this one stands out. "
            "The key differentiator is the attention to detail in the design. "
            "Battery life exceeded expectations by 20%.",
            score=9.0
        ),
        RankingExample(
            "Not impressed. The marketing promises more than it delivers. "
            "Build quality feels cheap and the instructions are confusing.",
            score=3.0
        ),
        RankingExample(
            "5 stars! Best purchase this year! My whole family loves it!",
            score=7.0  # Enthusiastic but not very informative
        ),
    ]
    
    # Train the model
    print("Training on review helpfulness scores...")
    learner.add_training_examples(training_reviews)
    
    # Optimize hyperparameters
    print("\nOptimizing Ridge regression parameters...")
    opt_results = learner.optimize_hyperparameters(
        alpha_range=[0.1, 1.0, 10.0, 100.0],
        cv_folds=3
    )
    print(f"Best alpha: {opt_results['best_alpha']}")
    
    # Train with best parameters
    metrics = learner.train(validation_split=0.3)
    print(f"\nTraining complete!")
    print(f"Validation R²: {metrics['val_r2']:.3f}")
    print(f"Cross-validation MSE: {metrics['cv_mse_mean']:.3f}")
    
    # Test on new reviews
    test_reviews = [
        "This product is absolutely terrible! It broke on the first day and the customer service was unhelpful. "
        "Save your money and buy something else. I'm returning mine immediately.",
        
        "I've been using this for 6 months now. Here's my detailed breakdown: "
        "Build Quality (4/5): Solid construction but some plastic parts feel cheap. "
        "Performance (5/5): Exceeds expectations, especially for the price point. "
        "Value (5/5): Best in its price range. "
        "Overall, highly recommended for budget-conscious buyers.",
        
        "Its good",
        
        "Meh. It's fine I guess. Nothing to complain about but nothing great either. "
        "Does what it says on the box.",
        
        "⭐⭐⭐⭐⭐ AMAZING!!! 💯 BEST EVER!!! 🔥🔥🔥",
        
        "After extensive testing in various conditions, I found this product performs well above average. "
        "The innovative design solves common problems found in similar products. "
        "Minor issue: the power button is poorly placed. "
        "Despite this, I'd purchase again.",
    ]
    
    print("\n=== Ranking New Reviews by Predicted Helpfulness ===\n")
    rankings = learner.rank_texts(test_reviews)
    
    for i, (review, score) in enumerate(rankings, 1):
        print(f"{i}. Helpfulness Score: {score:.2f}")
        print(f"   Review: {review[:100]}{'...' if len(review) > 100 else ''}")
        print()
    
    # Save the model
    learner.save_model("review_helpfulness_ranker.pkl")
    print("Model saved to 'review_helpfulness_ranker.pkl'")


def content_quality_scoring_demo():
    """Demo: Scoring content quality for moderation."""
    print("\n\n=== Content Quality Scoring Demo ===\n")
    
    learner = Qwen3EmbeddingValueLearner(
        embedding_dim=512,
        ridge_alpha=5.0
    )
    
    # Training data: Content with quality scores
    content_examples = [
        # High-quality content
        RankingExample(
            "Recent studies have shown that regular exercise can significantly improve cognitive function. "
            "A meta-analysis of 29 studies found that aerobic exercise increased hippocampal volume by 2%.",
            score=9.0
        ),
        RankingExample(
            "Here's a step-by-step guide to solving this problem: "
            "First, identify the key variables. Second, apply the relevant formula. "
            "Third, check your work by substituting back into the original equation.",
            score=8.5
        ),
        
        # Low-quality content
        RankingExample(
            "hey u guys should totally check this out its so coooool!!!!!!",
            score=2.0
        ),
        RankingExample(
            "This is spam. Click here for free money! Limited time offer!",
            score=0.5
        ),
        RankingExample(
            "idk what to write here but i need to post something",
            score=1.5
        ),
        
        # Medium quality
        RankingExample(
            "I think this topic is interesting. There are many different opinions about it.",
            score=4.0
        ),
        RankingExample(
            "Good point. I agree with most of what you said, though I'd add that context matters.",
            score=5.5
        ),
    ]
    
    learner.add_training_examples(content_examples)
    learner.train()
    
    # Score new content
    print("Scoring content quality for moderation...\n")
    
    test_content = [
        "The mitochondria is the powerhouse of the cell.",
        "URGENT: You've won $1000000! Click here now!",
        "Based on peer-reviewed research, we can conclude that this approach yields a 15% improvement.",
        "first post lol",
        "This is a thoughtful analysis of the situation, considering multiple perspectives.",
    ]
    
    for content in test_content:
        score = learner.predict(content)
        quality = "High" if score > 7 else "Medium" if score > 4 else "Low"
        print(f"Quality: {quality} (Score: {score:.2f})")
        print(f"Content: {content}")
        print()


def customer_support_prioritization_demo():
    """Demo: Prioritizing customer support tickets."""
    print("\n\n=== Customer Support Ticket Prioritization Demo ===\n")
    
    learner = Qwen3EmbeddingValueLearner(
        embedding_dim=384,
        ridge_alpha=1.0
    )
    
    # Training data: Support tickets with priority scores (0-10)
    support_tickets = [
        # Urgent issues
        RankingExample(
            "URGENT: Production server is down! All customers affected. Error 500 on all requests.",
            score=10.0
        ),
        RankingExample(
            "Cannot process payments. Getting 'Transaction Failed' for all customers since 2 hours ago.",
            score=9.5
        ),
        RankingExample(
            "Security breach detected. User data may be compromised. Need immediate assistance.",
            score=10.0
        ),
        
        # Medium priority
        RankingExample(
            "Feature request: Would be nice to have dark mode in the mobile app.",
            score=3.0
        ),
        RankingExample(
            "Bug report: Profile picture upload sometimes fails. Happens about 1 in 10 times.",
            score=5.0
        ),
        
        # Low priority
        RankingExample(
            "How do I change my password?",
            score=2.0
        ),
        RankingExample(
            "Thanks for the great service!",
            score=1.0
        ),
    ]
    
    learner.add_training_examples(support_tickets)
    learner.train()
    
    # Prioritize new tickets
    new_tickets = [
        "Help! I can't access my account and I have a presentation in 30 minutes!",
        "Suggestion: The homepage could use better colors.",
        "All data disappeared from my dashboard. This is critical for our operations.",
        "How do I export to PDF?",
        "System is showing incorrect calculations for financial reports. This could cause compliance issues.",
    ]
    
    print("Prioritizing support tickets...\n")
    priorities = learner.rank_texts(new_tickets)
    
    for ticket, priority_score in priorities:
        priority_level = "🔴 URGENT" if priority_score > 7 else "🟡 Medium" if priority_score > 4 else "🟢 Low"
        print(f"{priority_level} (Score: {priority_score:.1f})")
        print(f"Ticket: {ticket}")
        print()


if __name__ == "__main__":
    # Run all demos
    product_review_ranking_demo()
    content_quality_scoring_demo()
    customer_support_prioritization_demo()
    
    print("\n✅ All demos completed successfully!")