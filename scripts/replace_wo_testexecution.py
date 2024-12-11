import json
import os
from glob import glob
import shutil

def load_coverage_data(coverage_file_path):
    """Load the full test and method data from the coverage data JSON file."""
    with open(coverage_file_path, 'r') as f:
        data = json.load(f)
    
    coverage_data = {}
    for project in data["projects"]:
        project_name = project["name"]
        coverage_data[project_name] = {}
        
        for bug in project["bugs"]:
            bug_id = bug["bug_id"]
            coverage_data[project_name][bug_id] = {}

            for test in bug["tests"]:
                test_name = test["test_name"]
                test_body = test.get("test_body", "")
                method_data = {method["method_signature"]: method["method_body"] for method in test.get("covered_methods", [])}
                
                coverage_data[project_name][bug_id][test_name] = {
                    "test_body": test_body,
                    "covered_methods": method_data
                }
                
    return coverage_data

def replace_bodies(project_name, input_file, coverage_data, output_file):
    """Replace incomplete test and method bodies in the input file using coverage data and save to output."""
    with open(input_file, 'r') as f:
        data = json.load(f)

    bug_id = data["bug_id"]
    test_name = data["test_name"]

    # Check if coverage data exists for the specific project, bug, and test
    coverage_test_data = coverage_data.get(project_name, {}).get(bug_id, {}).get(test_name)
    
    if not coverage_test_data:
        print(f"No coverage data found for {project_name} Bug {bug_id} Test {test_name}.")
        # Copy the original file to the output folder if no coverage data is found
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        shutil.copy(input_file, output_file)
        print(f"Copied original JSON to {output_file}")
        return

    # Replace test body
    data["test_body"] = coverage_test_data["test_body"]

    # Replace each covered method body if the method exists in coverage data
    for method in data["covered_methods"]:
        method_signature = method["method_signature"]
        full_method_body = coverage_test_data["covered_methods"].get(method_signature)
        if full_method_body:
            method["method_body"] = full_method_body

    # Save the modified JSON data to the output file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Processed and saved {output_file}")

def process_project_files(project_name, project_folder, coverage_file, output_folder):
    """Process all test files in a project and replace incomplete data."""
    coverage_data = load_coverage_data(coverage_file)
    
    input_files = glob(os.path.join(project_folder, "*", "test_*.json"))
    for input_file in input_files:
        # Define output file path based on the input file structure
        relative_path = os.path.relpath(input_file, project_folder)
        output_file = os.path.join(output_folder, relative_path)
        replace_bodies(project_name, input_file, coverage_data, output_file)

# Define project and technique arrays
projects = ["Cli", "Math", "Csv", "Codec", "Compress", "Gson", "JacksonCore", "JacksonXml", "Mockito", "Jsoup", "Lang", "Time"]
# techs = ["one", "half", "zero", "minus_half", "minus_one"]
techs = ["depgraph"]

# Run the processing function for each combination of project and technique
for project in projects:
    for tech in techs:
        print(f"Processing {project} with technique {tech}...")

        # Define paths
        project_folder = f"../data/RankedData/{project}/{tech}"
        coverage_file = f"../data/CoverageData/backup/{project}_original_all_lines.json"
        output_folder = f"../data/WOTestExecution/{project}/{tech}"

        # Run the processing function
        process_project_files(project, project_folder, coverage_file, output_folder)
