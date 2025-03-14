import re
import os

def renumber_ideas_and_create_toc(input_filepath, output_filepath):
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_filepath}")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    renumbered_body_lines = []
    idea_titles_for_toc = []
    current_idea_count_for_body = 1
    
    # Regex to find lines starting with a number, a dot, and then a space.
    idea_pattern = re.compile(r"^(\s*)(\d+)(\.\s+)(.+)")

    for line in lines:
        match = idea_pattern.match(line)
        if match:
            leading_whitespace = match.group(1)
            # old_number = match.group(2) # Not needed for renumbering
            dot_and_space = match.group(3)
            idea_title_line = match.group(4).strip() # This is the actual title text for ToC
            
            # Store the title for ToC (original title, before renumbering in body)
            idea_titles_for_toc.append(idea_title_line)
            
            # Construct the new renumbered line for the main body
            new_body_line_content = f"{leading_whitespace}{current_idea_count_for_body}{dot_and_space}{idea_title_line}"
            
            # Preserve original line ending for the body line
            if line.endswith('\r\n'):
                new_body_line = new_body_line_content + '\r\n'
            elif line.endswith('\n'):
                new_body_line = new_body_line_content + '\n'
            else:
                new_body_line = new_body_line_content
            
            renumbered_body_lines.append(new_body_line)
            current_idea_count_for_body += 1
        else:
            # This line is not an idea starting line, so add it to the body as is
            renumbered_body_lines.append(line)
            
    # --- Create Table of Contents ---
    toc_lines = ["## Table of Contents\n\n"]
    for i, title in enumerate(idea_titles_for_toc):
        # ToC uses its own numbering, matching the final renumbered body
        toc_lines.append(f"{i + 1}. {title}\n")
    toc_lines.append("\n---\n\n") # Add a separator

    # Combine ToC and the renumbered body
    final_output_lines = toc_lines + renumbered_body_lines
            
    actual_ideas_found = len(idea_titles_for_toc)
    print(f"Found and renumbered {actual_ideas_found} ideas.")
    print(f"Generated a Table of Contents with {actual_ideas_found} entries.")

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.writelines(final_output_lines)
        print(f"Renumbered content with Table of Contents written to {output_filepath}")
    except Exception as e:
        print(f"Error writing output file: {e}")

# --- How to use ---
if __name__ == '__main__':
    input_file = "/Users/oscar/Downloads/3things_cleaned.md"
    # Output file will now contain the ToC at the beginning
    output_file_with_toc = "/Users/oscar/Downloads/3things_renumbered_with_toc.md" 
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file_with_toc}")
    
    renumber_ideas_and_create_toc(input_file, output_file_with_toc)