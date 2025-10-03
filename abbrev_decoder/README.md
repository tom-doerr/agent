# Abbreviation Decoder

A CLI tool that decodes abbreviated sentences where you only type the first letters of each word. Uses LLMs with logprobs and DSPy optimization to find the most likely full sentences.

## Quick Start

```bash
cd abbrev_decoder/

# Run the optimized decoder
./abbrev "wdyt"
# Output: what do you think

# Interactive mode
./abbrev -i

# Run optimization to improve performance
python abbrev_optimization_simple.py
```

## Features

- **Multiple implementations**: Both direct LLM and DSPy-optimized versions
- **Smart parsing**: Handles dots as separators (e.g., "h.a.y.d" → "how are you doing")
- **Multiple attempts**: Generates several candidates and ranks by likelihood
- **Interactive mode**: Real-time decoding as you type
- **JSON output**: Machine-readable format for integration
- **DSPy optimization**: Learn from examples to improve accuracy

## Installation

```bash
# Install dependencies
pip install litellm dspy openai

# Set up API key
export OPENROUTER_API_KEY="your-key-here"
```

## File Structure

```
abbrev_decoder/
├── abbrev                          # Main entry point (uses DSPy optimized version)
├── abbrev_decoder.py              # Original LLM implementation with logprobs
├── abbrev_decoder_dspy.py         # DSPy-based implementation
├── abbrev_dspy_program.py         # Core DSPy modules and signatures
├── abbrev_dataset.jsonl           # Training dataset (50+ examples)
├── abbrev_optimization_simple.py  # Optimization script
├── abbrev_expander_optimized.json # Saved optimized program
└── README.md                      # This file
```

## Usage Examples

### Basic Usage

```bash
# Single decode
./abbrev "wdyt"
# Output: what do you think

# With more attempts for difficult abbreviations
./abbrev "hayd.twirgt.wanriiapc" -a 20

# JSON output
./abbrev "tysm" -j
```

### Running Optimization

```bash
# Optimize the decoder with training data
python abbrev_optimization_simple.py

# The optimized program is automatically used by ./abbrev
```

### Direct Script Usage

```bash
# Use the original LLM version
./abbrev_decoder.py "wdyt"

# Use DSPy version explicitly
./abbrev_decoder_dspy.py "wdyt"
```

## Examples

```
wdyt → what do you think
htmtd → how to make this decision
hayd → how are you doing
tiavg → time is a valuable gift
plmk → please let me know
tysm → thank you so much
hdywmth → how do you want me to help
```

## How It Works

1. **Letter Parsing**: Extracts individual letters from the abbreviation
2. **Prompt Engineering**: Uses examples and context to guide the LLM
3. **Multiple Attempts**: Varies temperature and prompts for diversity
4. **Validation**: Ensures expansions match the abbreviation pattern
5. **Ranking**: Orders candidates by log probability or confidence
6. **DSPy Optimization**: Learns from examples to improve accuracy

## Models Supported

- OpenRouter models (Gemini Flash, GPT-3.5/4, etc.)
- OpenAI models (with OPENAI_API_KEY)
- Any LiteLLM-supported model

Default: `openrouter/google/gemini-2.0-flash-001` (fast and cost-effective)