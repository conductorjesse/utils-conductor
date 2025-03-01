# Industrial Process Flow Generator

This application generates detailed process flows for industrial processes based on reference class information. It uses the OpenAI o1-mini model to generate progressively more detailed descriptions of the process.

## Features

- Integrated search functionality to find reference classes
- Select from search results or enter custom reference class information
- Process the reference class through a pipeline of 3 prompts
- View the conversation history between each step
- Progress tracking through the generation pipeline
- Automatically save final process flow outputs to local files with UTF-8 encoding

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Get an OpenAI API key with access to the o1-mini model.

3. Set up your API key:
   - Create a `.env` file based on `.env.example` and add your OpenAI API key

4. Run the application:
   - Windows: Double-click `run_app.bat` or run `streamlit run app.py` in a command prompt
   - Linux/Mac: Run `./run_app.sh` or `streamlit run app.py` in a terminal

## How to Use

1. Search for reference classes in the sidebar search bar
2. Either:
   - Select a reference class from the search results dropdown, or
   - Enter your own custom reference class information in the fields below
3. Click "Start/Reset Process" to begin processing
4. Click "Continue to Next Step" after each step to move through the pipeline
5. The final output (from step 3) will be automatically saved to the "outputs" directory

## Prompt Pipeline

The application runs through 3 sequential prompts:

1. **Context Elaboration**: Takes the reference class information and elaborates on it, filling in missing details and returning a structured summary.
2. **Process Flow Description**: Generates a high-level process flow description with unit operations and streams.
3. **Mass-Balance Transformations**: Describes the stoichiometric or mass-balance transformations for each unit operation.

## Files

- `app.py`: Main application code
- `prompts.txt`: Contains the prompts used in the pipeline
- `product_list.csv`: Contains reference classes for industrial processes
- `requirements.txt`: Lists the required Python packages
- `run_app.bat`: Windows script to run the application
- `run_app.sh`: Unix/Linux script to run the application
- `.env.example`: Template for creating a `.env` file with your API key
- `outputs/`: Directory where process flow outputs are saved (UTF-8 encoded)

## Example Reference Class

Here's an example reference class:
```
Methanol,Natural Gas Reforming + Synthesis,"Syngas is generated from methane, then catalytically converted to methanol."
```

## Troubleshooting

- If you encounter API rate limiting, wait a few moments before continuing to the next step.
- Make sure your OpenAI API key has access to the o1-mini model.
- Check the "outputs" directory for saved files if they don't appear in the UI notification. 