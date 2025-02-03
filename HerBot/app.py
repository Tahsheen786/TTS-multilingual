#importing libraries
from extract_txt import read_files
from txt_processing import preprocess
from txt_to_features import txt_features, feats_reduce
from extract_entities import get_number, get_email, rm_email, rm_number, get_name, get_skills
from model import simil
import pandas as pd
import json
import os
import uuid
from flask import Flask, flash, request, redirect, url_for, render_template, send_file
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv
import PyPDF2
import requests
import google.generativeai as genai
from fpdf import FPDF
from flask import abort
import shutil
import io
import fitz  # PyMuPDF
from PIL import Image



#used directories for data, downloading and uploading files 
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files/resumes/')
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files/outputs/')
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data/')

# Make directory if UPLOAD_FOLDER does not exist
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# Make directory if DOWNLOAD_FOLDER does not exist
if not os.path.isdir(DOWNLOAD_FOLDER):
    os.mkdir(DOWNLOAD_FOLDER)
#Flask app config 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER
app.config['SECRET_KEY'] = 'nani?!'

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc','docx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/', methods=['GET'])
def main_page():
    return _show_page()
 
@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    app.logger.info(request.files)
    upload_files = request.files.getlist('file')
    app.logger.info(upload_files)
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if not upload_files:
        flash('No selected file')
        return redirect(request.url)
    for file in upload_files:
        original_filename = file.filename
        if allowed_file(original_filename):
            extension = original_filename.rsplit('.', 1)[1].lower()
            filename = str(uuid.uuid1()) + '.' + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_list = os.path.join(UPLOAD_FOLDER, 'files.json')
            files = _get_files()
            files[filename] = original_filename
            with open(file_list, 'w') as fh:
                json.dump(files, fh)
 
    flash('Upload succeeded')
    return redirect(url_for('upload_file'))
 
 
@app.route('/download/<code>', methods=['GET'])
def download(code):
    files = _get_files()
    if code in files:
        path = os.path.join(UPLOAD_FOLDER, code)
        if os.path.exists(path):
            return send_file(path)
    abort(404)
 
def _show_page():
    files = _get_files()
    return render_template('index.html', files=files)
 
def _get_files():
    file_list = os.path.join(UPLOAD_FOLDER, 'files.json')
    if os.path.exists(file_list):
        with open(file_list) as fh:
            return json.load(fh)
    return {}

def process_pdf(file_content):
    # Create a file-like object from the bytes content
    pdf_file_like = io.BytesIO(file_content)
    
    # Create a PDF file reader object
    pdf_reader = PyPDF2.PdfReader(pdf_file_like)

    # Extract text from the PDF
    text = ""
    for page_number in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_number].extract_text()

    return text

def clean_email(email):
    # Remove unwanted characters like square brackets
    return email.strip("[]'\"")

def send_email(recipient_emails, subject, message):
    for recipient_email in recipient_emails:
        clean_email_addr = clean_email(recipient_email)
        
        # Your email credentials
        sender_email = "tanishadhoot27@outlook.com"
        sender_password = "1437201@At"  # Use your app password here

        # Create message container
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = clean_email_addr
        msg['Subject'] = subject

        # Add message body
        msg.attach(MIMEText(message, 'plain'))

        try:
            # Connect to Outlook SMTP server
            server = smtplib.SMTP('smtp.office365.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)

            # Send email
            server.sendmail(sender_email, clean_email_addr, msg.as_string())
            print(f"Email sent successfully to {clean_email_addr}")

            # Close connection
            server.quit()

        except Exception as e:
            print(f"Error sending email to {clean_email_addr}: {e}")


os.environ["API_KEY"] = "AIzaSyDM7YwpW9GwomqqG7OiivqqYqCVWYJT7LA"

api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable not set.")


genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_interview_questions_from_skills(jdtxt):
    prompt = f"Generate interview questions for the following skills: {', '.join(jdtxt)}"
    
    try:
        response = model.generate_content(prompt)
         # Print the entire response object
        return response# Assuming the response contains a 'text' field with the questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        return None

def create_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    # Add content to the PDF
    for line in content.split('\n'):
        pdf.cell(0, 10, txt=line, ln=True, align='L')

    pdf.output(filename)



def extract_images_from_pdf_folder(pdf_folder_path, extracted_images_folder):
    # Ensure the output folder exists
    if not os.path.exists(extracted_images_folder):
        os.makedirs(extracted_images_folder)

    # Process each PDF file in the folder
    for filename in os.listdir(pdf_folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder_path, filename)
            print(f"Processing {pdf_path}...")

            try:
                # Open the PDF file
                doc = fitz.open(pdf_path)

                # Iterate through the pages
                for page_number in range(len(doc)):
                    page = doc.load_page(page_number)
                    
                    # Extract images from the page
                    for img_index, img in enumerate(page.get_images(full=True)):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_filename = f"{filename}_page_{page_number+1}_img_{img_index+1}.png"
                        image_path = os.path.join(extracted_images_folder, image_filename)

                        # Save the image
                        with open(image_path, "wb") as image_file:
                            image_file.write(image_bytes)
                        print(f"Image saved to {image_path}")

                doc.close()

            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")





@app.route('/process',methods=["POST"])
def process():
    if request.method == 'POST':

        rawtext = request.form['rawtext']
        jdtxt = [rawtext]
        resumetxt = read_files(UPLOAD_FOLDER)
        p_resumetxt = preprocess(resumetxt)
        p_jdtxt = preprocess(jdtxt)

        feats = txt_features(p_resumetxt, p_jdtxt)
        feats_red = feats_reduce(feats)

        df = simil(feats_red, p_resumetxt, p_jdtxt)

        t = pd.DataFrame({'Original Resume': resumetxt})
        dt = pd.concat([df, t], axis=1)

        dt['Phone No.'] = dt['Original Resume'].apply(lambda x: get_number(x))
        dt['E-Mail ID'] = dt['Original Resume'].apply(lambda x: get_email(x))

        dt['Original'] = dt['Original Resume'].apply(lambda x: rm_number(x))
        dt['Original'] = dt['Original'].apply(lambda x: rm_email(x))
        dt['Candidate\'s Name'] = dt['Original'].apply(lambda x: get_name(x))

        skills = pd.read_csv(DATA_FOLDER + 'skill_red.csv')
        skills = skills.values.flatten().tolist()
        skill = [z.lower() for z in skills]

        dt['Skills'] = dt['Original'].apply(lambda x: get_skills(x, skill))
        dt = dt.drop(columns=['Original', 'Original Resume'])
        sorted_dt = dt.sort_values(by=['JD 1'], ascending=False)

        sorted_dt_filtered = sorted_dt[sorted_dt['JD 1'] >= 0.001]

        interview_questions = generate_interview_questions_from_skills(jdtxt)

        if interview_questions:
            print("Generated Interview Questions:")
            print(interview_questions)
            if interview_questions._result and interview_questions._result.candidates:
                questions_text = interview_questions._result.candidates[0].content.parts[0].text
            else:
                questions_text = "No questions generated."

            # Define PDF file path
            pdf_filename = os.path.join(DOWNLOAD_FOLDER, "Interview_Questions.pdf")
            
            # Create the PDF
            create_pdf(questions_text, pdf_filename)
            print("Generated Interview Questions PDF:", pdf_filename)
        else:
            print("Error generating interview questions.")
            return "Error generating interview questions", 500

        # Save filtered data to CSV
        out_path = os.path.join(DOWNLOAD_FOLDER, "Candidates.csv")
        sorted_dt_filtered.to_csv(out_path, index=False)

        top_rankers = []
        with open(out_path, 'r') as file:
            reader = csv.DictReader(file)
            sorted_rankers = sorted(reader, key=lambda row: float(row['JD 1']), reverse=True)
            for row in sorted_rankers[:3]:
                top_rankers.append(row['E-Mail ID'])  # Append only the email address

        # Define directory for shortlisted resumes
        shortlisted_resumes_folder = os.path.join(DOWNLOAD_FOLDER, 'Shortlisted_Resumes/')
        if not os.path.isdir(shortlisted_resumes_folder):
            os.mkdir(shortlisted_resumes_folder)

        extracted_images_folder = os.path.join(DOWNLOAD_FOLDER, 'Extracted_Images/')
        if not os.path.isdir(extracted_images_folder):
            os.mkdir(extracted_images_folder)

        # Copy shortlisted resumes to the new folder
        for email in top_rankers:
            email_clean = clean_email(email)
            print(f"Processing email: {email_clean}")
            for filename in os.listdir(UPLOAD_FOLDER):
                if filename.endswith('.pdf') or filename.endswith('.docx') or filename.endswith('.doc'):
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    print(f"Checking file: {filename}")
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        text = process_pdf(file_content)
                        if email_clean in text:
                            print(f"Copying file: {filename}")
                            shutil.copy(file_path, shortlisted_resumes_folder)
                        else:
                            print(f"No match for email {email_clean} in file {filename}")
                            
        subject = "Congratulations on Your Selection!"
        message_template = """
        Dear Student,

        Congratulations! You have been selected as one of the top candidates for the position. We are excited to move forward with the hiring process. We will be in touch with you shortly with further details.

        Best regards,
        HR from CodeHerThing
        """

        # Send emails
        send_email(top_rankers, subject, message_template)
        pdf_folder_path = r"C:\Users\ROG\OneDrive\Desktop\MyBOT\files\outputs\Shortlisted_Resumes"
        extracted_images_folder = r"C:\Users\ROG\OneDrive\Desktop\MyBOT\files\outputs\Extracted_Images"
        # Test the function
        extract_images_from_pdf_folder(pdf_folder_path, extracted_images_folder)

        # Define paths for testing



        return send_file(out_path, as_attachment=True)

if __name__=="__main__":
    app.run(port=8080, debug=False) 