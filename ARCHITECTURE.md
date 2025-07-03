# AI Agent Framework Architecture

## Overview

This repository implements a sophisticated AI agent framework built on DSPy (Declarative Self-improving Language Programs). The architecture emphasizes modularity, safety, preference learning, and continuous improvement.

## Core Components

### 1. **Base Infrastructure**

#### `base_agent.py`
- **BaseAgent**: Abstract base class providing:
  - History management
  - Status tracking
  - Data persistence
- **CommandAgent**: Base for command-driven agents
- **BatchProcessingAgent**: Base for batch processing workflows

#### `config.py`
- Pydantic-based configuration management
- Environment variable overrides
- Validation for all settings
- Global configuration singleton

#### `utils/`
- **io.py**: Centralized NDJSON I/O operations
- **models.py**: Common DSPy model patterns and versioning

### 2. **Agent Implementations**

#### Production Agents
- **`ambient_agent.py`**: Autonomous agent that monitors RSS feeds, labels events, and makes judgments
- **`ranking_agent.py`**: Pairwise ranking system for learning user preferences
- **`local_agent.py`**: Interactive CLI agent with Vi keybindings and safety checks
- **`agent_simpledspy.py`**: SimpleDSPy-based agent with flexible command interface

#### Experimental/Research Agents
- **`nlco_iter.py`**: Natural Language Constraint Optimization - iterative refinement system
- **`iter_improvement.py`**: Multi-aspect critique and improvement system
- **`self_review_agent.py`**: Self-evaluation and improvement capabilities

### 3. **DSPy Modules** (`dspy_modules/` and `dspy_programs/`)

- **Value Networks**: Score prediction with uncertainty
- **Active Learning**: Uncertainty-based data collection
- **Memory GAN**: Generative memory management
- **Ranking Optimizer**: Advanced preference learning with multiple strategies

### 4. **Context & Integration**

#### `context_provider.py`
Provides rich context to agents:
- System information (memory, disk)
- Weather data (location-aware)
- Home automation status (SmartThings)

#### `home_automation.py` & `smartthings_client.py`
- SmartThings API integration
- Device discovery and control
- Natural language command parsing

## Data Flow Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User Input    │────▶│   Agent Layer    │────▶│   LLM Layer     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                           │
                               ▼                           ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │ Context Provider │     │  DSPy Modules   │
                        └──────────────────┘     └─────────────────┘
                               │                           │
                               ▼                           ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │   Data Layer     │     │ MLflow Tracking │
                        │  (.ndjson files) │     │   (Experiments) │
                        └──────────────────┘     └─────────────────┘
```

## Key Design Patterns

### 1. **Preference Learning Pipeline**
```
Ordered Data → Pairwise Examples → DSPy Training → Optimized Model
     ↓              ↓                    ↓               ↓
ranking_set    create_pairs()    BootstrapFewShot   Versioned Save
```

### 2. **Safety-First Command Execution**
- Command validation before execution
- User confirmation for dangerous operations
- Comprehensive logging

### 3. **Model Versioning**
- Timestamp-based versioning
- Symlinks to latest models
- Automatic cleanup of old versions

### 4. **Configuration Hierarchy**
```
Defaults → TOML File → Environment Variables → Runtime Override
```

## Module Dependencies

```
base_agent.py
    ↓
├── agent implementations (ambient_agent.py, etc.)
├── utils/io.py (NDJSON operations)
├── utils/models.py (DSPy patterns)
└── config.py (configuration)

context_provider.py
    ↓
├── weather API (wttr.in)
├── system info (subprocess)
└── home_automation.py → smartthings_client.py

dspy_ranking_optimizer.py
    ↓
├── utils/io.py
├── MLflow tracking
└── DSPy optimization
```

## Testing Strategy

- **Unit Tests**: Core functionality (`test_base_agent.py`, `test_config.py`)
- **Integration Tests**: Context providers (`test_context_provider.py`)
- **DSPy Module Tests**: Ranking and optimization (`test_dspy_ranking_optimizer.py`)

## Security Considerations

1. **API Tokens**: Stored in config files (gitignored) or environment variables
2. **Command Execution**: Safety checks and user confirmation
3. **File Access**: Restricted to designated directories
4. **Network Access**: Limited to configured APIs

## Performance Optimizations

1. **Parallel Processing**: DSPy parallel execution for LLM calls
2. **Caching**: Model predictions and API responses
3. **Batch Processing**: Efficient handling of multiple items
4. **Lazy Loading**: Models loaded only when needed

## Future Extensibility

The architecture supports easy extension through:
- New agent types (inherit from BaseAgent)
- Additional context providers
- Custom DSPy modules
- New data sources
- Alternative LLM providers

## Configuration Example

```toml
# nlco_config.toml
[weather]
enabled = true

[weather.location]
lat = 48.2667
lon = 10.9833
city = "Mering"

[smartthings]
token = "your-token-here"

[mlflow]
tracking_uri = "http://localhost:5002"

[model]
default_model = "deepseek/deepseek-reasoner"
max_tokens = 4000
temperature = 0.7
```