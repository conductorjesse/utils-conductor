# Process Flow Generator - Batch Processing

## Overview

This project generates process flow diagrams and analyses for industrial processes based on reference classes. It uses OpenAI and Claude APIs to generate detailed descriptions, mass-balance analyses, and structured data for process flows.

The codebase has been simplified to focus on the core functionality with minimal configuration. It processes reference classes defined in a CSV file and generates multiple outputs.

## Files

- `pipeline.py` - Core processing logic with LLM model configurations
- `gpt_utils.py` - Utilities for API calls to OpenAI and Claude
- `batch_processor.py` - Processes multiple reference classes from a CSV file
- `run_pipeline.py` - Processes a single reference class specified by ref_ID

## Prerequisites

- Python 3.8 or later
- Required packages (install via `pip install -r requirements.txt`):
  - pandas
  - openai
  - anthropic
  - python-dotenv
  - tqdm
- API keys:
  - OpenAI API key (set as environment variable `OPENAI_API_KEY`)
  - Claude API key (set as environment variable `ANTHROPIC_API_KEY`)

## Configuration

The system uses hardcoded defaults for simplicity:

- Input file: `batch_product_list.csv`
- Output directory: `outputs`
- Prompts file: `prompts.txt`
- Number of prompts: 5

## Input Format

The input CSV file (`batch_product_list.csv`) must contain:

- A `ref_ID` column with unique integer IDs
- At least three columns for product/system, method, and description (in that order)

Example:
```
ref_ID,Product/System,Production/Process Method,Brief Description
1,Ammonia,Haber-Bosch process,Production of ammonia from nitrogen and hydrogen
2,Polyethylene,High-pressure process,Production of polyethylene using high-pressure
```

## Prompt Configuration

The system is configured to use specific models for each prompt step:

1. **Context Elaboration** - OpenAI o1-mini
2. **Process Flow Description** - OpenAI o1-mini  
3. **Mass-Balance Analysis** - OpenAI o1
4. **JSON Structure Generation** - Claude sonnet
5. **Mermaid Diagram Generation** - OpenAI o1-mini

## Usage

### Processing a Single Reference Class

To process a single reference class, run:

```bash
python run_pipeline.py <ref_ID>
```

Where `<ref_ID>` is the ID of the reference class in the CSV file.

### Processing Multiple Reference Classes

To process all reference classes in the CSV file:

```bash
python batch_processor.py
```

The outputs will be saved in the `outputs` directory with the following naming format:
- Text outputs: `<ref_ID>_text_YYYYMMDD_HHMM.txt`
- JSON outputs: `<ref_ID>_json_YYYYMMDD_HHMM.txt`
- Mermaid diagram: `<ref_ID>_mermaid_YYYYMMDD_HHMM.txt`

## Outputs

For each reference class, the system generates:

1. **Context elaboration** - Detailed explanation of the industrial process
2. **Process flow description** - Step-by-step process flow
3. **Mass-balance analysis** - Analysis of mass flows (saved as text output)
4. **JSON structure** - Structured representation of the process flow (saved as JSON output)
5. **Mermaid diagram** - Code for a flowchart visualization (saved as mermaid output)

## Error Handling

The system includes error handling for:
- Missing API keys (displays warnings)
- Invalid reference IDs
- Missing CSV columns
- API call failures

## Extending the System

To modify the model configurations, edit the `PROMPT_CONFIG` list in `pipeline.py`.

To add more prompts, update:
1. The `prompts.txt` file with additional prompts
2. The `PROMPT_CONFIG` list in `pipeline.py`
3. Update the `NUM_PROMPTS` constant in the relevant files 