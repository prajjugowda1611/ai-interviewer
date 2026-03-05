import PyPDF2

def extract_resume_text(file_path):
    extracted_text = ""
    try:
        # Open the PDF in 'read binary' mode
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            
            # Loop through every page and extract the text
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"
                
        return extracted_text
    
    except FileNotFoundError:
        return "Error: Could not find the resume file. Check the name and location."

# --- Test the Engine ---
if __name__ == "__main__":
    print("Booting up the Document Scanner...\n")
    
    # Run the function on your file
    my_resume = extract_resume_text("resume.pdf")
    
    # Print the first 500 characters just to prove it worked
    print("SUCCESS! Here is a preview of what the AI will see:")
    print("-" * 50)
    print(my_resume[:500])
    print("-" * 50)