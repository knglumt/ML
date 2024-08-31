import os
import ollama
from datetime import datetime
import csv
import re

def split_and_clean_code_file(file_path, output_folder_path):
    
    with open(file_path, 'r') as file:
        content = file.read()

    first_assessment_pos = content.find('/** ASSESSMENT')
    
    if first_assessment_pos != 0:
        before_assessment = content[:first_assessment_pos].strip()
        content = content[first_assessment_pos:] 
        #content = f"/** ASSESSMENT */\n{before_assessment}\n{content}"  
        
    # Determine whether to remove scores and feedback based on the filename
    remove_comments = 'refcode' not in os.path.basename(file_path).lower()
    
    # Split the content based on the /** ASSESSMENT comment
    if remove_comments:
        sections = re.split(r'/\*\* ASSESSMENT.*?\*/', content, flags=re.DOTALL)
    else:
        pattern = r'(/\*\* ASSESSMENT.*?\*/)(.*?)(?=\s/\*\* ASSESSMENT|$)'
        matches = re.finditer(pattern, content, flags=re.DOTALL)
        sections = []
        for match in matches:
            comment_block, text = match.groups()
            sections.append(f'{comment_block}\n{text.strip()}')
    
    # Process each section
    for i, section in enumerate(sections):

        if (first_assessment_pos != 0) and (i == 1):
            section = f"\n{before_assessment}\n{section}"
          
        
        cleaned_section = section.strip()

        if not cleaned_section:
            continue
        
        if remove_comments:
            inx = i
        else:
            inx = i + 1

        segment_folder_path = os.path.join(output_folder_path, f'segment_{inx}')
        os.makedirs(segment_folder_path, exist_ok=True)

        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        output_file_path = os.path.join(segment_folder_path, f'{base_filename}_segment_{inx}.txt')

        with open(output_file_path, 'w') as output_file:
            output_file.write(cleaned_section)
            
def process_code_files(base_folder_path):
    
    os.makedirs(base_folder_path, exist_ok=True)
    
    for filename in os.listdir(base_folder_path):
        if filename.endswith(('.txt', '.java', '.cpp')): 
            file_path = os.path.join(base_folder_path, filename)
            split_and_clean_code_file(file_path, base_folder_path)

# Function to read code files from the folder
def read_code_files(folder_path):
    code_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt") or filename.endswith(".java") or filename.endswith(".cpp"):
            with open(os.path.join(folder_path, filename), 'r') as file:
                code = file.read()
                code_files.append((filename, code))
    return code_files

# Function to create the assessment prompt
def create_assessment_prompt(student_code, ref_codes):
    refcode_details = "\n\n".join([f"Reference Code ({i+1}):\n{code}" for i, code in enumerate(ref_codes)])
    prompt = (
        "You are an AI designed to assess entry-level programming exams at an academic level. "
        "Your expertise lies in segmenting the answer codes based on the most similar reference code, assessing each segment of code under the \"ASSESSMENT\" comments "
        "and grading it based on the grade in the most similar reference code. "
        "You can use both dynamic and static code assessment. "
        "You can also use abstract syntax trees, control flow graphs, and data flow graphs of each segment to make assessments properly. "
        "Your main goal is to assess the code like an instructor and grade it even if it is not correct totally. "
        "Follow the steps below.\n\n"
        "Step 1 - Perform an assessment for the entire code at once and create only one grade by comparing the answer code to the reference code.\n"
        "Step 2 - Assess and grade the codes by using dynamic and static code assessment methods.\n"
        "Step 3 - Support your assessment by comparing codes using their graph models; abstract syntax trees, control flow graphs, and data flow graphs.\n"
        "Step 4 - Grades should be integer and not bigger than the reference code's segment grade.\n\n"
        "Step 5 - Do not show titles and any extra details in your answer. Provide only the final grade.\n\n"
        f"Reference Codes:\n{refcode_details}\n\n"
        f"Student Code:\n{student_code}\n\n"
    )
    return prompt

# Function to create and use Ollama Client with persistent session
def assess_code_with_client(client, student_code, ref_codes):
    prompt = create_assessment_prompt(student_code, ref_codes)
    
    try:
        response = client.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.1, 'top_p': 0.1},
            stream=True,
        )

        result_text = ""
        for chunk in response:
            result_text += chunk['message']['content']
        
        return result_text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error occurred during assessment."

# Assess all code files and store the results
def assess_all_code_files(folder_path):
    code_files = read_code_files(folder_path)
    ref_codes = [(filename, code) for filename, code in code_files if filename.lower().startswith("refcode")]
    student_codes = [(filename, code) for filename, code in code_files if not filename.lower().startswith("refcode")]
    results = []

    # Create a persistent Ollama client
    client = ollama.Client() 

    for filename, code in student_codes:
        assessment = assess_code_with_client(client, code, [ref_code for _, ref_code in ref_codes])
        print((filename[:-4]) + " " + assessment)
        results.append((filename[:-4], assessment))
    
    return results

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath("__file__"))
    folder_name = input("Enter the folder name: ")
    folder_path = os.path.join(current_dir, folder_name)

    if not os.path.exists(folder_path):
        print("Folder does not exist!")
    else:
        
        # Split code file into segments data\Midterm2-Annotated (1)\Q1
        process_code_files(folder_path)
        
        # Stop = input("Continue!")
        
        for root, dirs, files in os.walk(folder_path):
            for dir_name in dirs:
                if "segment" in dir_name.lower():  # Check if the folder name includes "segment"
                    print(datetime.now().strftime("%Y%m%d_%H%M%S"))
                    segment_folder_path = os.path.join(root, dir_name)
                    print(f"Assessing folder: {segment_folder_path}")
                    results = assess_all_code_files(segment_folder_path)
                    print(datetime.now().strftime("%Y%m%d_%H%M%S"))
                    print(results)
                
                    # Process the results for CSV output
                    processed_data = [result.split() for filename, result in results]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(segment_folder_path, f"assessment_{timestamp}.csv")
                
                    with open(filename, mode='w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerows(processed_data)
                
                    print(f"Data has been written to {filename}")
