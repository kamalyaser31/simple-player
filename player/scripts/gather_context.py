import os

def gather_context(root_dir, output_file, extensions=('.py',)):
    """Gathers file paths and contents for Gemini context."""
    for root, dirs, files in os.walk(root_dir):
        # Skip common non-source directories
        if any(d in root for d in ['.git', '__pycache__', 'venv', '.idea', '.vscode']):
            continue
            
        for file in files:
            if file.endswith(extensions):
                full_path = os.path.abspath(os.path.join(root, file))
                output_file.write(f"{full_path}\n")
                output_file.write("```" + (file.split('.')[-1] if '.' in file else "") + "\n")
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        output_file.write(f.read() + "\n")
                except Exception as e:
                    output_file.write(f"Error reading file: {e}\n")
                output_file.write("```\n\n")

if __name__ == "__main__":
    # Run this from your project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_filename = "context.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        gather_context(project_root, f)
    print(f"Context gathered into {output_filename}")