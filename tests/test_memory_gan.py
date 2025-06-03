import pytest
from unittest.mock import patch, MagicMock
from memory_gan_optimizer import main, get_firecrawl_content, gan_metric

@pytest.fixture
def mock_firecrawl(monkeypatch):
    # Mock Firecrawl responses
    mock_app = MagicMock()
    mock_app.scrape_url.return_value = {"content": "Test content"}
    monkeypatch.setattr("memory_gan_optimizer.firecrawl.FirecrawlApp", lambda _: mock_app)

@pytest.fixture
def mock_dspy(monkeypatch):
    # Mock DSPy modules and responses
    mock_predict = MagicMock()
    mock_predict.return_value = MagicMock(
        challenging_question="Test question",
        answer="Test answer",
        reference_answer="Test reference"
    )
    
    monkeypatch.setattr("memory_gan_optimizer.dspy.Predict", mock_predict)
    monkeypatch.setattr("memory_gan_optimizer.dspy.settings.configure", MagicMock())

@pytest.fixture
def mock_mlflow(monkeypatch):
    # Mock MLflow
    monkeypatch.setattr("memory_gan_optimizer.mlflow.start_run", MagicMock())
    monkeypatch.setattr("memory_gan_optimizer.mlflow.log_params", MagicMock())
    monkeypatch.setattr("memory_gan_optimizer.mlflow.log_metric", MagicMock())
    monkeypatch.setattr("memory_gan_optimizer.mlflow.set_tag", MagicMock())

def test_main(mock_firecrawl, mock_dspy, mock_mlflow, capsys):
    # Run the optimizer
    main()
    
    # Capture output
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify expected output
    assert "Starting MemoryGAN SIMBA Optimization" in output
    assert "Validation Results" in output or "Skipping validation" in output

def test_get_firecrawl_content(mock_firecrawl):
    # Test Firecrawl content retrieval
    content = get_firecrawl_content("https://example.com")
    assert content == "Test content"

def test_gan_metric():
    # Test metric calculation
    example = MagicMock()
    pred = MagicMock()
    pred.source_text = "Test source"
    pred.question = "Test question"
    pred.memory_answer = "Wrong answer"
    pred.reference_answer = "Correct answer"
    
    # Mock assessment prediction
    mock_assess = MagicMock()
    mock_assess.assessment_score = "0.75"
    
    with patch("memory_gan_optimizer.dspy.Predict", return_value=mock_assess):
        score = gan_metric(example, pred)
        assert score == 0.75
    
    # Test error handling
    with patch("memory_gan_optimizer.dspy.Predict", side_effect=Exception):
        score = gan_metric(example, pred)
        assert score == 0.0
