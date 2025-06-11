import pytest
pytestmark = pytest.mark.timeout(10, method='thread')
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dspy_modules.memory_gan import main, get_firecrawl_content, gan_metric, optimize_memory_gan

@pytest.fixture
def mock_firecrawl(monkeypatch):
    # Mock Firecrawl responses
    mock_app = MagicMock()
    mock_app.scrape_url.return_value = {"content": "Test content"}
    monkeypatch.setattr("dspy_modules.memory_gan.firecrawl.FirecrawlApp", lambda *args, **kwargs: mock_app)

@pytest.fixture
def mock_dspy(monkeypatch):
    # Mock DSPy modules and responses
    mock_predict = MagicMock()
    mock_predict.return_value = MagicMock(
        challenging_question="Test question",
        answer="Test answer",
        reference_answer="Test reference"
    )
    
    # Mock SIMBA optimizer
    mock_simba = MagicMock()
    mock_simba.return_value.train.return_value = MagicMock()
    
    monkeypatch.setattr("dspy_modules.memory_gan.dspy.Predict", mock_predict)
    monkeypatch.setattr("dspy_modules.memory_gan.dspy.settings.configure", MagicMock())
    monkeypatch.setattr("dspy_modules.memory_gan.SIMBA", mock_simba)

@pytest.fixture(autouse=True)
def mock_mlflow(monkeypatch):
    """Mock all MLflow operations to prevent external connections"""
    monkeypatch.setattr("dspy_modules.memory_gan.mlflow.set_experiment", MagicMock())
    monkeypatch.setattr("dspy_modules.memory_gan.mlflow.start_run", MagicMock())
    monkeypatch.setattr("dspy_modules.memory_gan.mlflow.log_params", MagicMock())
    monkeypatch.setattr("dspy_modules.memory_gan.mlflow.log_metric", MagicMock())
    monkeypatch.setattr("dspy_modules.memory_gan.mlflow.set_tag", MagicMock())
    monkeypatch.setattr("dspy_modules.memory_gan.mlflow.end_run", MagicMock())

def test_main(mock_firecrawl, mock_dspy, capsys):
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
    mock_assess.assessment_score = "1.0"
    
    with patch("dspy_modules.memory_gan.dspy.Predict", return_value=mock_assess):
        score = gan_metric(example, pred)
        assert score == 1.0
    
    # Test error handling
    with patch("dspy_modules.memory_gan.dspy.Predict", side_effect=Exception):
        score = gan_metric(example, pred)
        assert score == 0.0
        
    # Test invalid score parsing
    mock_assess.assessment_score = "invalid"
    with patch("dspy_modules.memory_gan.dspy.Predict", return_value=mock_assess):
        score = gan_metric(example, pred)
        assert score == 0.0

def test_optimize_memory_gan(mock_dspy):
    import dspy
    # Mock trainset
    trainset = [dspy.Example(source_text="Test source").with_inputs("source_text")]
    
    # Test optimization
    optimized = optimize_memory_gan(trainset)
    assert optimized is not None
    
    # Get the SIMBA mock from the fixture setup
    mock_simba = mock_dspy.args[0].return_value  # The mock_simba instance
    
    # Verify SIMBA was instantiated with expected parameters
    mock_dspy.args[0].assert_called_once_with(
        metric=gan_metric,
        max_steps=2,
        max_demos=4,
        bsize=2
    )
    
    # Verify train was called with the trainset
    mock_simba.train.assert_called_once_with(trainset=trainset)
