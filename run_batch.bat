@echo off
REM Batch file to run the batch processor on Windows
REM Usage: run_batch.bat [input_file] [output_dir] [prompts_file] [max_workers]

echo Running Batch Processor...

IF "%1"=="" (
    python run_batch.py
) ELSE (
    IF "%2"=="" (
        python run_batch.py --input %1
    ) ELSE (
        IF "%3"=="" (
            python run_batch.py --input %1 --output %2
        ) ELSE (
            IF "%4"=="" (
                python run_batch.py --input %1 --output %2 --prompts %3
            ) ELSE (
                python run_batch.py --input %1 --output %2 --prompts %3 --workers %4
            )
        )
    )
)

echo Batch processing complete! 