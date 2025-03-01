import os
import re
import time
import datetime
import json
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv

# Import our utilities for LLM calls
import gpt_utils

# Load environment variables
load_dotenv()

# Define the prompt configuration - clearly shows which provider/model for each prompt
PROMPT_CONFIG = [
    # Prompt 1: Context Elaboration
    {"step": "Context Elaboration", "provider": "openai", "model": "o1-mini", "temperature": 1},
    
    # Prompt 2: Process Flow Description 
    {"step": "Process Flow Description", "provider": "openai", "model": "o1-mini", "temperature": 1},
    
    # Prompt 3: Mass-Balance Analysis
    {"step": "Mass-Balance Analysis", "provider": "openai", "model": "o1-mini", "temperature": 1},
    
    # Prompt 4: JSON Structure Generation
    {"step": "JSON Structure Generation", "provider": "claude", "model": "sonnet", "temperature": 1},
    
    # Prompt 5: Mermaid Diagram Generation
    {"step": "Mermaid Diagram Generation", "provider": "claude", "model": "sonnet", "temperature": 1}
]

def load_prompts(filename: str, num_prompts: int = 5) -> List[str]:
    """Load prompts from a text file."""
    prompts = []
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        # Split by 'Prompt X ---' pattern
        prompt_sections = re.split(r'Prompt \d+ ---\n\n', content)
        # Skip the first empty section if it exists
        if prompt_sections[0].strip() == '':
            prompt_sections = prompt_sections[1:]
        # Get the requested number of prompts
        prompts = [p.strip() for p in prompt_sections[:num_prompts]]
    
    if len(prompts) < num_prompts:
        raise ValueError(f"Expected {num_prompts} prompts, but found {len(prompts)}.")
    
    return prompts

def save_output(
    output_dir: str, 
    reference_info: str, 
    output: str, 
    ref_id: Optional[int] = None, 
    step: Optional[int] = None,
    output_type: str = "text"
) -> str:
    """Save output to a file with appropriate formatting."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Format timestamp in the requested format: YYYYMMDD_HHMM
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # New naming convention: <ref ID>_<step>_<date/time>
    if ref_id is not None:
        # Determine step name or number
        if step is not None:
            step_identifier = f"step{step}"
        else:
            # For final outputs, use the output type as the step identifier
            step_identifier = output_type.lower()
        
        # Create filename with the new format
        filename = f"{output_dir}/{ref_id}_{step_identifier}_{timestamp}.txt"
    else:
        # Fallback for cases without a ref_id
        product = reference_info.split(',')[0]
        product = re.sub(r'[^\w\s]', '', product).strip().replace(' ', '_')
        if step is not None:
            step_identifier = f"step{step}"
        else:
            step_identifier = output_type.lower()
        filename = f"{output_dir}/{product}_{step_identifier}_{timestamp}.txt"
    
    # Write to file - specify UTF-8 encoding to handle Unicode characters
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f"Reference Class: {reference_info}\n\n")
        if step is not None:
            step_names = [config["step"] for config in PROMPT_CONFIG]
            if 0 <= step-1 < len(step_names):
                file.write(f"Step {step} - {step_names[step-1]}:\n")
            else:
                file.write(f"Step {step}:\n")
        else:
            file.write(f"Process Flow {output_type}:\n")
        file.write(output)
    
    return filename

def process_reference_class(
    reference_info: str, 
    ref_id: Optional[int] = None,
    prompts_file: str = "prompts.txt", 
    output_dir: str = "outputs", 
    save_all_steps: bool = True,
    num_prompts: int = 5
) -> List[str]:
    """
    Process a single reference class through all prompts.
    
    Args:
        reference_info: Information about the reference class (comma-separated string)
        ref_id: Reference ID for file naming
        prompts_file: Path to the prompts file
        output_dir: Directory to save outputs
        save_all_steps: Whether to save intermediate steps
        num_prompts: Number of prompts to process (default: 5)
        
    Returns:
        List of responses for each step
    """
    # Load prompts
    prompts = load_prompts(prompts_file, num_prompts)
    
    # Initialize conversation history and results
    conversation = []
    output_results = []
    
    print(f"Processing reference class: {reference_info}" + (f" (ref_ID: {ref_id})" if ref_id is not None else ""))
    
    # Process each prompt according to the configuration
    for step, (prompt_text, config) in enumerate(zip(prompts, PROMPT_CONFIG), 1):
        if step > num_prompts:
            break
            
        print(f"Step {step}: {config['step']}")
        print(f"  Using {config['provider']} model: {config['model']}")
        
        try:
            # Replace placeholder for context elaboration
            if step == 1:
                prompt_text = prompt_text.replace("{{reference class information}}", reference_info)
            
            # Call the appropriate API based on provider
            if config['provider'] == 'openai':
                response = gpt_utils.call_openai(
                    prompt=prompt_text,
                    model=config['model'],
                    temperature=config['temperature'],
                    previous_messages=conversation
                )
            else:  # claude
                response = gpt_utils.call_claude(
                    prompt=prompt_text,
                    model=config['model'],
                    temperature=config['temperature'],
                    previous_messages=conversation
                )
            
            # Update conversation history
            conversation.append({"role": "user", "content": prompt_text})
            conversation.append({"role": "assistant", "content": response})
            
            output_results.append(response)
            
            # Save output for this step using the new naming convention
            save_output(output_dir, reference_info, response, ref_id, step=step)
            
        except Exception as e:
            print(f"Error in {config['step']} step: {str(e)}")
            output_results.append(f"Error: {str(e)}")
            break
    
    print(f"Processing complete. Results saved to {os.path.abspath(output_dir)} directory.")
    return output_results

if __name__ == "__main__":
    # Simple direct usage example
    process_reference_class(
        reference_info="Ammonia,Haber-Bosch process,Production of ammonia from nitrogen and hydrogen",
        ref_id=42,
        output_dir="outputs",
        save_all_steps=True
    ) 