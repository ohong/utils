import re
import os

def clean_3things_doc(input_filepath, output_filepath):
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_filepath}")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    extracted_content = []
    capturing_ideas = False
    current_idea_number = 0 # Tracks the number of the idea being captured (1, 2, 3, etc.)

    # Pattern to identify the start of a numbered idea
    start_idea_pattern = re.compile(r"^\s*(\d+)\.\s+(.+)")

    # Patterns that strongly indicate non-idea content or the end of an idea block.
    # These lines will be excluded, and they will stop the capture of an ongoing idea block.
    block_stopper_patterns = [
        re.compile(r"^\s*Happy Sunday!", re.IGNORECASE),
        re.compile(r"^\s*Thanks for reading 3 Things!", re.IGNORECASE),
        re.compile(r"^\s*Subscribe for free to receive new posts", re.IGNORECASE),
        re.compile(r"^\s*email\s*$", re.IGNORECASE), # Line is exactly "email"
        re.compile(r"^\s*password\s*$", re.IGNORECASE), # Line is exactly "password"
        re.compile(r"^\s*oscar\.hong2015@gmail\.com\s*$", re.IGNORECASE), # Specific email example
        re.compile(r"^\s*Subscribe\s*$", re.IGNORECASE), # Line is exactly "Subscribe"
        re.compile(r"^\s*Share 3 Things", re.IGNORECASE),
        re.compile(r"^\s*That’s all for today!", re.IGNORECASE),
        re.compile(r"^\s*That’s all for this week", re.IGNORECASE),
        re.compile(r"^\s*~ Elaine", re.IGNORECASE),
        re.compile(r"^\s*[A-Za-z]+\s\d{1,2},\s\d{4}\s*$", re.IGNORECASE), # Date line, e.g., "Mar 12, 2023"
        re.compile(r"^\s*Elaine Zelby\s*$", re.IGNORECASE), # Author byline, often under a date
        re.compile(r"^\s*Coming soon", re.IGNORECASE),
        re.compile(r"^\s*Substack is a platform", re.IGNORECASE),
        re.compile(r"^\s*© \d{4} Elaine Zelby", re.IGNORECASE), # Copyright
        re.compile(r"^\s*View archive", re.IGNORECASE),
        re.compile(r"^\s*Start writing", re.IGNORECASE),
        re.compile(r"^\s*Get the app", re.IGNORECASE),
        re.compile(r"^\s*Substack is the home for great culture", re.IGNORECASE),
        re.compile(r"^\s*\d+ Likes\s*$", re.IGNORECASE), # e.g., "7 Likes"
        re.compile(r"^\s*And in case you like podcasts…", re.IGNORECASE),
        re.compile(r"^\s*If you liked what you read please share", re.IGNORECASE),
        re.compile(r"^\s*I’m excited to share an update", re.IGNORECASE),
        re.compile(r"^\s*I’m having a blast and have two of the absolute best co-founders", re.IGNORECASE),
        re.compile(r"^\s*I wanted to share a quick update", re.IGNORECASE),
        re.compile(r"^\s*Each edition of 3 Things will contain", re.IGNORECASE)
    ]

    for line_num, line_content in enumerate(lines):
        line_stripped = line_content.strip()
        original_line = line_content # Keep original line with leading/trailing whitespace for output

        is_stopper = False
        if line_stripped: # Only check non-empty lines for stoppers
            for pattern in block_stopper_patterns:
                if pattern.match(line_stripped):
                    is_stopper = True
                    break
        
        # Special check for the email/password/subscribe block structure
        if line_stripped.lower() == "email" and line_num + 2 < len(lines):
            next_line_stripped = lines[line_num+1].strip().lower()
            third_line_stripped = lines[line_num+2].strip().lower()
            if next_line_stripped == "password" and ("@" in third_line_stripped or third_line_stripped == "subscribe"):
                is_stopper = True # This whole block is a stopper sequence

        if is_stopper:
            if capturing_ideas: # If we were capturing, this stopper ends the block
                if extracted_content and extracted_content[-1].strip() != "":
                    extracted_content.append("\n") # Add a newline for separation
            capturing_ideas = False
            current_idea_number = 0
            continue # Skip adding this stopper line to output

        match = start_idea_pattern.match(original_line)
        if match:
            idea_num_in_line = int(match.group(1))
            
            if not capturing_ideas and idea_num_in_line == 1:
                # Start of a new block of ideas (e.g., "1. ...")
                if extracted_content and extracted_content[-1].strip() != "":
                     extracted_content.append("\n") # Ensure separation from previous text
                capturing_ideas = True
                current_idea_number = idea_num_in_line
                extracted_content.append(original_line)
            elif capturing_ideas and idea_num_in_line == current_idea_number + 1:
                # Continues the current sequence of ideas (e.g., "2. ..." after "1. ...")
                current_idea_number = idea_num_in_line
                extracted_content.append(original_line)
            elif capturing_ideas and idea_num_in_line == 1:
                # A new "1. ..." encountered while already capturing (ends previous block, starts new)
                if extracted_content and extracted_content[-1].strip() != "":
                    extracted_content.append("\n")
                current_idea_number = idea_num_in_line # Reset for the new block
                extracted_content.append(original_line)
            else:
                # Numbered line, but breaks sequence or is not a "1." to start a new block
                if capturing_ideas: # Stop capturing current block
                    if extracted_content and extracted_content[-1].strip() != "":
                        extracted_content.append("\n")
                capturing_ideas = False
                current_idea_number = 0
                # Check if this line itself is a "1." to start a new capture
                if idea_num_in_line == 1:
                    capturing_ideas = True
                    current_idea_number = idea_num_in_line
                    extracted_content.append(original_line)

        elif capturing_ideas:
            # This line is part of the current idea's content
            # Avoid adding multiple consecutive blank lines from source
            if line_stripped == "" and extracted_content and extracted_content[-1].strip() == "":
                pass
            else:
                extracted_content.append(original_line)
        # If not capturing and not a start_idea_pattern and not a stopper, the line is ignored.

    # Post-process to clean up excessive newlines
    final_output_lines = []
    if extracted_content:
        # Join and then split to handle newlines consistently, then filter
        full_text = "".join(extracted_content)
        split_lines = full_text.splitlines(keepends=True)
        
        prev_line_was_blank = True # Start as if preceded by a blank to trim leading blanks
        for L in split_lines:
            current_line_is_blank = (L.strip() == "")
            if current_line_is_blank and prev_line_was_blank:
                continue # Skip multiple blank lines
            final_output_lines.append(L)
            prev_line_was_blank = current_line_is_blank
        
        # Remove trailing blank lines from the very end of the document
        while final_output_lines and final_output_lines[-1].strip() == "":
            final_output_lines.pop()

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.writelines(final_output_lines)
        print(f"Cleaned content written to {output_filepath}")
        if not final_output_lines:
            print("Warning: No content was extracted. The output file is empty. Check patterns if this is unexpected.")
    except Exception as e:
        print(f"Error writing output file: {e}")

# --- How to use ---
# 1. Save the code above as a Python file (e.g., cleaner_script.py) in a convenient location.
# 2. Open a terminal or command prompt.
# 3. Navigate to the directory where you saved cleaner_script.py.
# 4. Run the script by calling the function with your file paths.
#    You can add these lines at the end of the script (outside the function definition)
#    to make it run when you execute the file:

if __name__ == '__main__':
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct input and output paths relative to the user's Downloads folder
    # This assumes the script is NOT in the Downloads folder itself, adjust if needed.
    # For simplicity, using absolute paths as provided by the user.
    input_file = "/Users/oscar/Downloads/3things.md"
    output_file = "/Users/oscar/Downloads/3things_cleaned.md"
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    clean_3things_doc(input_file, output_file)