import os
import sys
import pandas as pd
import concurrent.futures
from tqdm import tqdm
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import our pipeline module
from pipeline import process_reference_class

# Load environment variables (API keys)
load_dotenv()

# Default settings - hardcoded for simplicity
INPUT_FILE = "batch_product_list.csv"
OUTPUT_DIR = "outputs"
PROMPTS_FILE = "prompts.txt"
NUM_PROMPTS = 5
SAVE_ALL_STEPS = True
MAX_WORKERS = 5  # Number of concurrent processes

def load_reference_classes(file_path: str) -> pd.DataFrame:
    """
    Load reference classes from a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame containing reference classes
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        raise ValueError(f"Error loading CSV file: {str(e)}")

def process_reference_class_wrapper(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper function to process a single reference class with error handling.
    
    Args:
        args: Dictionary of arguments for process_reference_class
        
    Returns:
        Dictionary containing processing results and reference information
    """
    ref_id = args.get("ref_id")
    reference_info = args.get("reference_info")
    
    try:
        results = process_reference_class(
            reference_info=reference_info,
            ref_id=ref_id,
            prompts_file=args.get("prompts_file"),
            output_dir=args.get("output_dir"),
            save_all_steps=args.get("save_all_steps"),
            num_prompts=args.get("num_prompts")
        )
        return {
            "ref_id": ref_id,
            "reference_info": reference_info,
            "success": True,
            "outputs": results
        }
    except Exception as e:
        return {
            "ref_id": ref_id,
            "reference_info": reference_info,
            "success": False,
            "error": str(e)
        }

def main():
    """Main function to run the batch processor."""
    print(f"Starting batch processing with {INPUT_FILE}")
    
    # Check if OpenAI and Claude API keys are set
    openai_key = os.environ.get('OPENAI_API_KEY')
    claude_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not openai_key:
        print("WARNING: OPENAI_API_KEY not found in environment variables.")
    if not claude_key:
        print("WARNING: ANTHROPIC_API_KEY not found in environment variables.")
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load the reference classes from CSV
    try:
        df = load_reference_classes(INPUT_FILE)
        
        # Check if ref_ID column exists
        if 'ref_ID' not in df.columns:
            print("Error: CSV file must contain a 'ref_ID' column.")
            return
        
        # Create a list of tasks to process
        tasks = []
        for _, row in df.iterrows():
            # Get the reference ID
            ref_id = row['ref_ID']
            
            # Build the reference info string from the first three columns
            # Assumes columns are in order: product/system, method, description
            if len(df.columns) >= 3:
                reference_info = ",".join(str(row[col]) for col in df.columns[:3])
            else:
                # Fallback: use all columns except ref_ID
                cols = [col for col in df.columns if col != 'ref_ID']
                reference_info = ",".join(str(row[col]) for col in cols)
            
            # Add the task arguments
            tasks.append({
                "ref_id": ref_id,
                "reference_info": reference_info,
                "prompts_file": PROMPTS_FILE,
                "output_dir": OUTPUT_DIR,
                "save_all_steps": SAVE_ALL_STEPS,
                "num_prompts": NUM_PROMPTS
            })
        
        # Process the reference classes in parallel
        results = []
        successful = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Create a progress bar
            for result in tqdm(executor.map(process_reference_class_wrapper, tasks), total=len(tasks)):
                results.append(result)
                if result.get("success", False):
                    successful += 1
        
        # Print the results
        print(f"\nProcessing complete: {successful}/{len(tasks)} reference classes processed successfully.")
        print(f"Results saved to {os.path.abspath(OUTPUT_DIR)} directory.")
        
        # Print any errors
        errors = [r for r in results if not r.get("success", False)]
        if errors:
            print(f"\nErrors encountered for {len(errors)} reference classes:")
            for e in errors:
                print(f"ref_ID {e['ref_id']}: {e.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    main() 