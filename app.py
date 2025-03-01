import streamlit as st
import pandas as pd
import openai
import os
import json
from typing import List, Dict, Any
import re
from dotenv import load_dotenv
import datetime
import time

# Load environment variables
load_dotenv()

# Load prompts from prompts.txt
def load_prompts(filename: str) -> List[str]:
    prompts = []
    with open(filename, 'r') as file:
        content = file.read()
        # Split by 'Prompt X ---' pattern
        prompt_sections = re.split(r'Prompt \d+ ---\n\n', content)
        # Skip the first empty section if it exists
        if prompt_sections[0].strip() == '':
            prompt_sections = prompt_sections[1:]
        # We only want the first 3 prompts as per requirement
        prompts = [p.strip() for p in prompt_sections[:3]]
    return prompts

# Load reference classes from CSV
def load_reference_classes(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    return df

# Save output to a file
def save_output(reference_info: str, output: str, index: int = None):
    # Create an outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # Format timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create a filename with timestamp and reference info
    if index is not None:
        filename = f"outputs/process_flow_{index}_{timestamp}.txt"
    else:
        # Extract product name from reference info and sanitize for filename
        product = reference_info.split(',')[0]
        product = re.sub(r'[^\w\s]', '', product).strip().replace(' ', '_')
        filename = f"outputs/process_flow_{product}_{timestamp}.txt"
    
    # Write to file - specify UTF-8 encoding to handle Unicode characters
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f"Reference Class: {reference_info}\n\n")
        file.write("Process Flow Analysis:\n")
        file.write(output)
    
    return filename

# Function to call OpenAI API
def call_openai_api(prompt: str, previous_messages: List[Dict[str, str]] = None) -> str:
    if previous_messages is None:
        previous_messages = []
    
    messages = previous_messages + [{"role": "user", "content": prompt}]
    
    # Use API key from .env file
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Add a loader with a placeholder
    progress_placeholder = st.empty()
    
    # Show loading state
    with progress_placeholder.container():
        progress_text = "Calling OpenAI API..."
        progress_bar = st.progress(0)
        for i in range(100):
            # Simulate progress while waiting for API response
            time.sleep(0.01)
            progress_bar.progress(i + 1)
    
    try:
        response = openai.Client(api_key=api_key).chat.completions.create(
            model="o1-mini",
            messages=messages,
        )
        result = response.choices[0].message.content
    except Exception as e:
        result = f"Error calling OpenAI API: {str(e)}"
    
    # Clear the loader
    progress_placeholder.empty()
    
    return result

# Main application
def main():
    st.set_page_config(page_title="Process Flow Generator", page_icon="🏭", layout="wide")
    
    st.title("Industrial Process Flow Generator")
    
    # Initialize session state for storing conversation
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
        
    if 'prompts' not in st.session_state:
        st.session_state.prompts = load_prompts("prompts.txt")
        
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
        
    if 'df' not in st.session_state:
        st.session_state.df = load_reference_classes("product_list.csv")
        
    if 'output_results' not in st.session_state:
        st.session_state.output_results = []
        
    if 'reference_info' not in st.session_state:
        st.session_state.reference_info = ""
        
    if 'reference_index' not in st.session_state:
        st.session_state.reference_index = None

    # Sidebar for configuration
    with st.sidebar:
        st.subheader("Reference Class Selection")
        
        # Search bar for reference classes
        search_term = st.text_input("Search reference classes", "")
        
        # Filter dataframe based on search term
        filtered_df = st.session_state.df
        if search_term:
            filtered_df = st.session_state.df[
                st.session_state.df['Product/System'].str.contains(search_term, case=False) |
                st.session_state.df['Production/Process Method'].str.contains(search_term, case=False) |
                st.session_state.df['Brief Description'].str.contains(search_term, case=False)
            ]
        
        reference_class_info = ""
        
        # Display the filtered CSV data
        if not filtered_df.empty:
            st.dataframe(filtered_df.head(10), use_container_width=True)
            
            # Select a row by index
            selected_indices = filtered_df.index.tolist()
            selected_index = st.selectbox(
                "Select a reference class",
                options=selected_indices,
                format_func=lambda x: f"{filtered_df.loc[x, 'Product/System']} - {filtered_df.loc[x, 'Production/Process Method']}"
            )
            
            selected_row = filtered_df.loc[selected_index]
            
            # Format the reference class information
            reference_class_info = f"{selected_row['Product/System']},{selected_row['Production/Process Method']},{selected_row['Brief Description']}"
            
            st.markdown("**Selected Reference Class:**")
            st.markdown(f"**Product/System:** {selected_row['Product/System']}")
            st.markdown(f"**Production Method:** {selected_row['Production/Process Method']}")
            st.markdown(f"**Description:** {selected_row['Brief Description']}")
            
            # Store the reference index
            st.session_state.reference_index = selected_index
        else:
            st.warning("No reference classes match your search. You can enter a custom one below.")
        
        # Divider
        st.markdown("---")
        
        # Custom reference class option
        st.subheader("Or Enter Custom Reference Class")
        custom_product = st.text_input("Product/System", "")
        custom_method = st.text_input("Production/Process Method", "")
        custom_description = st.text_area("Brief Description", "")
        
        # If custom fields are filled, use those instead
        if custom_product and custom_method and custom_description:
            reference_class_info = f"{custom_product},{custom_method},{custom_description}"
            st.session_state.reference_index = None
            
            # Show confirmation of custom reference class
            st.success("Using custom reference class")
        
        # Store the reference info
        if reference_class_info:
            st.session_state.reference_info = reference_class_info
        
        # Start/Reset button
        api_key = os.getenv("OPENAI_API_KEY")
        start_button_disabled = not (reference_class_info and api_key)
        
        if st.button("Start/Reset Process", disabled=start_button_disabled):
            st.session_state.conversation = []
            st.session_state.current_step = 0
            st.session_state.output_results = []
            # Replace the placeholder with actual reference class info in the first prompt
            first_prompt = st.session_state.prompts[0].replace("{{reference class information}}", reference_class_info)
            
            with st.spinner("Processing initial prompt..."):
                response = call_openai_api(first_prompt)
                
            # Store the prompt and response
            st.session_state.conversation.append({"role": "user", "content": first_prompt})
            st.session_state.conversation.append({"role": "assistant", "content": response})
            st.session_state.output_results.append(response)
            st.session_state.current_step = 1
            st.rerun()
    
    # Main content area for displaying conversation
    if st.session_state.conversation:
        # Add a progress indicator
        steps = ["Context Elaboration", "Process Flow Description", "Mass-Balance Analysis"]
        current_step = min(st.session_state.current_step, 3)
        
        # Display header with reference class info
        if st.session_state.reference_info:
            reference_parts = st.session_state.reference_info.split(',')
            if len(reference_parts) >= 2:
                index_display = f"Index: {st.session_state.reference_index}" if st.session_state.reference_index is not None else ""
                st.header(f"{reference_parts[0]} via {reference_parts[1]}")
                if index_display:
                    st.subheader(index_display)
        
        st.markdown("## Process Flow Generation Progress")
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown(f"**Step {current_step}/3:**")
        with col2:
            progress_bar = st.progress(current_step / 3)
            
        if current_step > 0 and current_step <= 3:
            st.info(f"Current phase: {steps[current_step-1]}")
        
        st.markdown("---")
        
        # Display each step in its own expander
        for i in range(0, len(st.session_state.conversation), 2):
            if i < len(st.session_state.conversation):
                step_num = i//2 + 1
                with st.expander(f"Step {step_num}", expanded=(step_num == st.session_state.current_step)):
                    st.markdown("**Prompt:**")
                    st.markdown(st.session_state.conversation[i]["content"])
                    
                    st.markdown("**Response:**")
                    response = st.session_state.conversation[i+1]["content"]
                    st.markdown(response)
        
        # If we haven't completed all 3 steps, show the "Continue" button
        if st.session_state.current_step < 3:
            if st.button("Continue to Next Step"):
                current_prompt = st.session_state.prompts[st.session_state.current_step]
                
                # For prompts after the first one, we need to reference the previous result
                messages_for_context = st.session_state.conversation.copy()
                
                with st.spinner(f"Processing step {st.session_state.current_step + 1}..."):
                    response = call_openai_api(current_prompt, previous_messages=messages_for_context)
                
                # Store the prompt and response
                st.session_state.conversation.append({"role": "user", "content": current_prompt})
                st.session_state.conversation.append({"role": "assistant", "content": response})
                st.session_state.output_results.append(response)
                st.session_state.current_step += 1
                
                # If we've completed all steps, save the output
                if st.session_state.current_step == 3:
                    output_file = save_output(
                        st.session_state.reference_info, 
                        response, 
                        st.session_state.reference_index
                    )
                    st.success(f"Process flow analysis saved to {output_file}")
                
                st.rerun()

if __name__ == "__main__":
    main() 