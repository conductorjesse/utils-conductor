#!/usr/bin/env python
"""
Wrapper script to run the batch processor from the root directory.
This script makes it easier to run the batch processor with the new directory structure.
"""

import os
import sys
import argparse
import importlib.util

def main():
    """Run the batch processor."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the batch processor")
    parser.add_argument("--input", "-i", default="data/batch_product_list.csv",
                        help="Path to the input CSV file (default: data/batch_product_list.csv)")
    parser.add_argument("--output", "-o", default="outputs",
                        help="Directory to save outputs (default: outputs)")
    parser.add_argument("--prompts", "-p", default="src/pfd-gen/prompts.txt",
                        help="Path to the prompts file (default: src/pfd-gen/prompts.txt)")
    parser.add_argument("--workers", "-w", type=int, default=5,
                        help="Number of concurrent workers (default: 5)")
    args = parser.parse_args()
    
    # Import the batch processor
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Modify the environment with our settings
    os.environ["INPUT_FILE"] = args.input
    os.environ["OUTPUT_DIR"] = args.output
    os.environ["PROMPTS_FILE"] = args.prompts
    os.environ["MAX_WORKERS"] = str(args.workers)
    
    # Import and run batch_processor
    # Using importlib to handle module with dash in name
    spec = importlib.util.spec_from_file_location(
        "batch_processor", 
        os.path.join(os.path.dirname(__file__), "src/pfd-gen/batch_processor.py")
    )
    batch_processor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(batch_processor)
    batch_processor.main()

if __name__ == "__main__":
    main() 