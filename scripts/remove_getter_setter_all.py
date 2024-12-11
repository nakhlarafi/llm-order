import json
import os
import shutil
import sys

def load_json(file_path):
    """Load a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    """Save the modified JSON back to file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def is_getter_or_setter(method_signature):
    """Check if a method is a getter or setter based on typical naming conventions."""
    getter_prefixes = ['get', 'is', 'has']
    setter_prefixes = ['set']
    
    method_name = method_signature.split(":")[-1].split('(')[0]
    return any(method_name.startswith(prefix) for prefix in getter_prefixes + setter_prefixes)


def is_getter_or_setter_and_short(method):
    """Check if a method is a getter or setter and has 3 or fewer lines of code."""
    method_signature = method['method_signature']
    method_body = method.get('method_body', '')

    getter_prefixes = ['get', 'is', 'has']
    setter_prefixes = ['set']

    method_name = method_signature.split(":")[-1].split('(')[0]
    is_getter_setter = any(method_name.startswith(prefix) for prefix in getter_prefixes + setter_prefixes)
    
    # Count the number of lines in the method body
    num_lines = method_body.count('\n') + 1  # Count lines based on newline characters
    less_than_3_lines = (is_getter_setter and num_lines <= 3)
    return less_than_3_lines, num_lines


def filter_getter_setter_methods(sbfl_file, output_file, proj_name, bug_id, test_id):
    # Load the JSON file
    sbfl_data = load_json(sbfl_file)

    # Filter out getter or setter methods in sbfl_data and print the details
    remaining_methods = []
    for method in sbfl_data['covered_methods']:
        less_than_3_lines, num_lines = is_getter_or_setter_and_short(method)
        if not less_than_3_lines:
            remaining_methods.append(method)
        else:
            method_name = method['method_signature'].split(":")[-1].split('(')[0]
            print(f"Project: {proj_name}, Bug ID: {bug_id}, Test ID: {test_id}, Removing Getter/Setter Method: {method_name}, has {num_lines} lines")

    sbfl_data['covered_methods'] = remaining_methods

    # Fix the method_id of the remaining methods
    for i, method in enumerate(sbfl_data['covered_methods']):
        method['method_id'] = i

    # Save the modified sbfl file to the new location
    save_json(sbfl_data, output_file)

def process_all_tests_without_getter_setter(base_dir, projects, techniques):
    """Process all tests for multiple projects and techniques and filter out getter/setter methods."""
    for project in projects:
        for tech in techniques:
            print(f"Processing Project: {project}, Technique: {tech}")
            sbfl_dir = os.path.join(base_dir, project, tech)
            output_dir = os.path.join(base_dir, project, f'wo_gettersetter_{tech}')

            # Copy the directory structure to the new folder (without files)
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            shutil.copytree(sbfl_dir, output_dir, dirs_exist_ok=True)

            # Iterate over bug ID directories
            for bug_id in os.listdir(sbfl_dir):
                sbfl_bug_dir = os.path.join(sbfl_dir, bug_id)
                output_bug_dir = os.path.join(output_dir, bug_id)

                # Iterate over the test JSON files in the sbfl directory
                for sbfl_file_name in os.listdir(sbfl_bug_dir):
                    sbfl_file = os.path.join(sbfl_bug_dir, sbfl_file_name)
                    output_file = os.path.join(output_bug_dir, sbfl_file_name)

                    # Extract project name and test ID from file path or content (assuming filename contains the test ID)
                    proj_name = project
                    test_id = os.path.splitext(sbfl_file_name)[0]

                    # Process the JSON file to remove getter/setter methods
                    filter_getter_setter_methods(sbfl_file, output_file, proj_name, bug_id, test_id)

# Example usage:
# Define the base directory, projects, and techniques
base_dir = '../data/RankedData'
projects = ["Cli", "Math", "Csv", "Codec", "Gson", "JacksonCore", "JacksonXml", "Mockito", "Compress", "Jsoup", "Lang", "Time"]
# techniques = ["ochiai", "depgraph", "execution", "perfect", "random"]
techniques = ["perfect_callgraph"]

process_all_tests_without_getter_setter(base_dir, projects, techniques)
