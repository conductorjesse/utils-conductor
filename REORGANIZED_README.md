# Process Flow Diagram Generator - Reorganized Structure

This README describes the reorganized directory structure and how to run the system after the reorganization.

## Directory Structure

The codebase has been reorganized into the following structure:

```
.
├── data/                   # Input data files
│   ├── batch_product_list.csv
│   └── product_list.csv
├── outputs/                # Main output directory
├── src/                    # Source code
│   ├── pfd-gen/            # Process Flow Diagram generator
│   │   ├── pipeline.py     # Main pipeline for processing reference classes
│   │   ├── batch_processor.py # Batch processing script
│   │   └── prompts.txt     # Prompts for the pipeline
│   ├── utils/              # Utility functions
│   │   └── gpt_utils.py    # Utilities for calling LLMs
│   └── visuals/            # Visualization code
├── vis outputs/            # Visualization outputs
│   ├── step4/              # Step 4 output copies (JSON structures)
│   └── step5/              # Step 5 output copies (Mermaid diagrams)
├── .env                    # Environment variables (API keys)
├── requirements.txt        # Python dependencies
├── run_batch.py            # Wrapper script to run batch processing
└── app.py                  # Main application
```

## Running the Batch Processor

To run the batch processor with the new directory structure, use the `run_batch.py` script:

```sh
# Run with default settings
python run_batch.py

# Run with custom input file
python run_batch.py --input data/your_custom_file.csv

# Run with custom output directory
python run_batch.py --output custom_outputs

# Run with all custom settings
python run_batch.py --input data/your_file.csv --output custom_outputs --prompts src/pfd-gen/custom_prompts.txt --workers 3
```

## Input Format

The input CSV file must contain the following columns:
- `ref_ID`: A unique identifier for each reference class
- At least one additional column with the reference class information

Example:
```csv
ref_ID,product,method,description
1,Ammonia,Haber-Bosch,Production of ammonia from nitrogen and hydrogen
2,Ethylene,Steam cracking,Thermal cracking of hydrocarbons to produce ethylene
```

## Output Files

The system generates output files with the following naming convention:
- `index#_date/time_step#.txt`

For example: `42_20240302_1215_step4.txt`

Output files are saved in:
- All outputs: `outputs/` directory
- Step 4 (JSON Structure) copies: `vis outputs/step4/` directory
- Step 5 (Mermaid Diagram) copies: `vis outputs/step5/` directory

## Environment Variables

Make sure your `.env` file contains the necessary API keys:
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Troubleshooting

If you encounter import errors, make sure you're running scripts from the root directory of the project. 