import os
from IPython.display import display, Markdown
from google.colab import files
import google.generativeai as genai

# Import ReportLab modules for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import black, blue, darkgreen

# --- User Input Function ---

def get_user_input():
    """
    Prompts the user for their Google Gemini API key and details
    required for resume and cover letter generation.
    Handles ValueError for numeric inputs.
    """
    print("--- AI Resume & Cover Letter Generator ---")
    print("This tool will help you generate a resume and cover letter using an AI model.")
    print("Please provide the requested information.")

    api_key = input("Enter your Google Gemini API Key: ").strip()
    if not api_key:
        print("API Key cannot be empty. Please restart and provide a valid key.")
        return None

    job_title = input("Enter the Job Title you are applying for: ").strip()
    company_name = input("Enter the Company Name: ").strip()
    your_name = input("Enter your Full Name: ").strip()
    your_email = input("Enter your Email Address: ").strip()
    your_phone = input("Enter your Phone Number: ").strip()
    your_linkedin = input("Enter your LinkedIn Profile URL (optional): ").strip()

    print("\n--- Your Work Experience ---")
    experiences = []
    while True:
        try:
            num_experiences = int(input("How many work experiences do you want to include? "))
            break
        except ValueError:
            print("Invalid input. Please enter a number for the quantity of work experiences.")

    for i in range(num_experiences):
        print(f"\nExperience {i+1}:")
        exp_title = input("Job Title: ").strip()
        exp_company = input("Company: ").strip()
        exp_dates = input("Start Date - End Date (e.g., Jan 2020 - Dec 2022): ").strip()
        exp_responsibilities = input("Key Responsibilities/Achievements (comma-separated): ").strip().split(',')
        experiences.append({
            'title': exp_title,
            'company': exp_company,
            'dates': exp_dates,
            'responsibilities': [r.strip() for r in exp_responsibilities if r.strip()]
        })

    print("\n--- Your Education ---")
    education_list = []
    while True:
        try:
            num_education = int(input("How many educational qualifications do you want to include? "))
            break
        except ValueError:
            print("Invalid input. Please enter a number for the quantity of educational qualifications.")

    for i in range(num_education):
        print(f"\nEducation {i+1}:")
        edu_degree = input("Degree/Qualification: ").strip()
        edu_institution = input("Institution: ").strip()
        edu_dates = input("Graduation Date (e.g., May 2023): ").strip()
        education_list.append({
            'degree': edu_degree,
            'institution': edu_institution,
            'dates': edu_dates
        })

    skills = input("\n--- Your Skills (comma-separated, e.g., Python, Machine Learning, Data Analysis): ").strip().split(',')
    skills = [s.strip() for s in skills if s.strip()]

    print("\n--- Cover Letter Specifics ---")
    hiring_manager_name = input("Enter the Hiring Manager's Name (optional): ").strip()
    how_heard = input("How did you hear about this position? (optional): ").strip()
    additional_cover_letter_points = input("Any additional points for the cover letter (e.g., specific projects, passion): ").strip()

    user_data = {
        'api_key': api_key,
        'job_title': job_title,
        'company_name': company_name,
        'your_name': your_name,
        'your_email': your_email,
        'your_phone': your_phone,
        'your_linkedin': your_linkedin,
        'experiences': experiences,
        'education': education_list,
        'skills': skills,
        'hiring_manager_name': hiring_manager_name,
        'how_heard': how_heard,
        'additional_cover_letter_points': additional_cover_letter_points
    }
    return user_data

# --- AI Model Interaction with Google Gemini Only ---

def generate_text_with_ai(prompt, api_key):
    """
    Connects to the Google Gemini API and generates text based on the provided prompt.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error communicating with AI: {e}"

def generate_resume_content(user_data):
    """
    Constructs a detailed prompt for the AI to generate resume content.
    """
    resume_prompt = f"""
    Generate a professional resume for {user_data['your_name']} applying for a {user_data['job_title']} position at {user_data['company_name']}.

    Contact Information:
    Name: {user_data['your_name']}
    Email: {user_data['your_email']}
    Phone: {user_data['your_phone']}
    LinkedIn: {user_data['your_linkedin']}

    Summary/Objective: Write a concise professional summary highlighting key skills and career goals relevant to the {user_data['job_title']} role.

    Work Experience:
    Provide detailed bullet points for each experience, focusing on achievements and quantifiable results.
    """
    for exp in user_data['experiences']:
        resume_prompt += f"\n- Job Title: {exp['title']}"
        resume_prompt += f"\n  Company: {exp['company']}"
        resume_prompt += f"\n  Dates: {exp['dates']}"
        for resp in exp['responsibilities']:
            resume_prompt += f"\n  - {resp}"

    resume_prompt += "\n\nEducation:"
    for edu in user_data['education']:
        resume_prompt += f"\n- Degree: {edu['degree']}"
        resume_prompt += f"\n  Institution: {edu['institution']}"
        resume_prompt += f"\n  Graduation Date: {edu['dates']}"

    resume_prompt += f"\n\nSkills: {', '.join(user_data['skills'])}"
    resume_prompt += "\n\nFormat the resume clearly with sections like 'Contact Information', 'Summary', 'Work Experience', 'Education', and 'Skills'. Use bullet points for responsibilities and achievements."

    print("\nGenerating Resume...")
    return generate_text_with_ai(resume_prompt, user_data['api_key'])

def generate_cover_letter_content(user_data):
    """
    Constructs a detailed prompt for the AI to generate cover letter content.
    """
    cover_letter_prompt = f"""
    Write a professional cover letter for {user_data['your_name']} applying for the {user_data['job_title']} position at {user_data['company_name']}.

    Address the letter to {user_data['hiring_manager_name'] if user_data['hiring_manager_name'] else 'Hiring Manager'}.

    Key details to include:
    - Express enthusiasm for the {user_data['job_title']} role.
    - Briefly highlight relevant experience and skills from the following:
      {', '.join([exp['title'] + ' at ' + exp['company'] for exp in user_data['experiences']])}
      Skills: {', '.join(user_data['skills'])}
    - Connect your qualifications to the company's needs or the job description (imagine typical requirements for this job title).
    - Mention how you heard about the position: {user_data['how_heard'] if user_data['how_heard'] else 'online posting'}.
    - Include any additional points: {user_data['additional_cover_letter_points']}
    - Professional closing.

    Ensure the tone is professional, confident, and tailored to the specific role and company.
    """
    print("Generating Cover Letter...")
    return generate_text_with_ai(cover_letter_prompt, user_data['api_key'])


# --- PDF Generation Function ---

def create_pdf(filename, content_text, user_data, title="Document", is_cover_letter=False):
    """
    Generates a PDF document from the given text content using ReportLab.
    Includes highly revised parsing for resume sections based on observed AI output patterns.
    """
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Modify existing ReportLab styles to fit resume/cover letter needs
    styles['Heading1'].fontSize = 16
    styles['Heading1'].leading = 18
    styles['Heading1'].spaceBefore = 12
    styles['Heading1'].spaceAfter = 6
    styles['Heading1'].fontName = 'Helvetica-Bold'
    styles['Heading1'].alignment = TA_LEFT # Align headings to left by default

    styles['Heading2'].fontSize = 14
    styles['Heading2'].leading = 16
    styles['Heading2'].spaceBefore = 10
    styles['Heading2'].spaceAfter = 5
    styles['Heading2'].fontName = 'Helvetica-Bold'
    styles['Heading2'].alignment = TA_LEFT # Align subheadings to left

    # Add custom paragraph styles, inheriting properties from base styles
    styles.add(ParagraphStyle(name='TitleStyle',
                             parent=styles['Title'],
                             fontSize=24,
                             leading=28,
                             alignment=TA_CENTER,
                             spaceAfter=20))

    styles.add(ParagraphStyle(name='BodyTextCustom',
                             parent=styles['BodyText'],
                             fontSize=10,
                             leading=12,
                             spaceAfter=6,
                             alignment=TA_JUSTIFY))

    styles.add(ParagraphStyle(name='ListItem',
                             parent=styles['Bullet'],
                             fontSize=10,
                             leading=12,
                             leftIndent=0.3*inch,
                             spaceAfter=3))

    styles.add(ParagraphStyle(name='ContactInfoCentered', # Specific for Contact info
                             parent=styles['Normal'],
                             fontSize=10,
                             leading=12,
                             alignment=TA_CENTER,
                             spaceAfter=6)) # Add space after contact lines

    styles.add(ParagraphStyle(name='AddressLine', # For cover letter address lines
                             parent=styles['Normal'],
                             fontSize=10,
                             leading=12,
                             spaceAfter=3,
                             alignment=TA_LEFT))

    styles.add(ParagraphStyle(name='Signature',
                             parent=styles['Normal'],
                             fontSize=10,
                             leading=12,
                             spaceBefore=20,
                             alignment=TA_LEFT))


    if not is_cover_letter: # Logic for Resume PDF generation
        lines = content_text.split('\n')

        # --- Stage 1: Process Introductory/Contact/Summary Block ---
        intro_block_processed = False

        contact_info_line_index = -1
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if user_data['your_name'].lower() in stripped_line.lower() and ('@' in stripped_line or 'linkedin.com' in stripped_line):
                contact_info_line_index = i
                break

        if contact_info_line_index != -1:
            # 1. Add Name (centered, bold)
            story.append(Paragraph(f"<b>{user_data['your_name']}</b>", styles['TitleStyle']))
            story.append(Spacer(1, 0.05 * inch))

            # 2. Add Contact Info (centered)
            contact_line_content = lines[contact_info_line_index].strip()
            contact_line_content = contact_line_content.replace(user_data['your_name'], '').strip()
            contact_line_content = contact_line_content.replace("(Highly Recommended)", "").strip()

            contact_parts = [p.strip() for p in contact_line_content.split('|') if p.strip()]
            if contact_parts:
                story.append(Paragraph(" | ".join(contact_parts), styles['ContactInfoCentered']))
                story.append(Spacer(1, 0.1 * inch))

            # 3. Add Summary
            summary_start_index = -1
            summary_end_index = -1

            for i in range(contact_info_line_index + 1, len(lines)):
                stripped_line = lines[i].strip()
                if stripped_line.lower() == "summary":
                    summary_start_index = i
                elif summary_start_index != -1 and stripped_line.lower() in ["work experience", "education", "skills", "projects"]: # Removed "awards"
                    summary_end_index = i
                    break

            if summary_start_index != -1:
                summary_text_lines = []
                start_collecting = False
                for i in range(summary_start_index + 1, (summary_end_index if summary_end_index != -1 else len(lines))):
                    stripped_line = lines[i].strip()
                    if stripped_line:
                        summary_text_lines.append(stripped_line)

                if summary_text_lines:
                    story.append(Paragraph("<b>SUMMARY</b>", styles['Heading1']))
                    story.append(Paragraph(" ".join(summary_text_lines), styles['BodyTextCustom']))
                    story.append(Spacer(1, 0.2 * inch))

            intro_block_processed = True

        # --- Stage 2: Process Main Content Sections (Work Experience, Education, Skills, Projects) ---
        start_line_for_main_content = contact_info_line_index + 1
        if intro_block_processed and summary_end_index != -1:
            start_line_for_main_content = summary_end_index
        elif intro_block_processed:
             start_line_for_main_content = contact_info_line_index + 1
             for i in range(start_line_for_main_content, len(lines)):
                 if lines[i].strip().lower() in ["work experience", "education", "skills", "projects"]: # Removed "awards"
                     start_line_for_main_content = i
                     break


        current_section = None
        for i in range(start_line_for_main_content, len(lines)):
            line = lines[i]
            stripped_line = line.strip()
            if not stripped_line:
                continue

            # Section Headers
            if stripped_line.lower() == "work experience":
                current_section = "WORK EXPERIENCE"
                story.append(Paragraph("<b>WORK EXPERIENCE</b>", styles['Heading1']))
                story.append(Spacer(1, 0.1 * inch))
            elif stripped_line.lower() == "education":
                current_section = "EDUCATION"
                story.append(Paragraph("<b>EDUCATION</b>", styles['Heading1']))
                story.append(Spacer(1, 0.1 * inch))
            elif stripped_line.lower() == "skills":
                current_section = "SKILLS"
                story.append(Paragraph("<b>SKILLS</b>", styles['Heading1']))
                story.append(Spacer(1, 0.1 * inch))
            elif stripped_line.lower() == "projects":
                current_section = "PROJECTS"
                story.append(Paragraph("<b>PROJECTS</b>", styles['Heading1']))
                story.append(Spacer(1, 0.1 * inch))

            # Content parsing within sections
            elif current_section == "WORK EXPERIENCE":
                if ' | ' in stripped_line and any(term in stripped_line.lower() for term in ["strategist", "developer", "engineer", "analyst", "manager"]):
                    job_title_parts = stripped_line.split(' | ')
                    if len(job_title_parts) >= 3:
                        story.append(Paragraph(f"<b>{job_title_parts[0]}</b> | {job_title_parts[1]}", styles['Heading2']))
                        story.append(Paragraph(f"<i>{job_title_parts[2]}</i>", styles['BodyTextCustom']))
                    else:
                        story.append(Paragraph(stripped_line, styles['Heading2']))
                elif stripped_line.startswith('*'):
                    story.append(Paragraph(stripped_line, styles['ListItem']))
                else:
                    story.append(Paragraph(stripped_line, styles['BodyTextCustom']))

            elif current_section == "EDUCATION":
                if ' | ' in stripped_line:
                    edu_parts = stripped_line.split(' | ')
                    story.append(Paragraph(f"<b>{edu_parts[0]}</b>", styles['Heading2']))
                    story.append(Paragraph(edu_parts[1], styles['BodyTextCustom']))
                elif stripped_line.lower().startswith('graduated:'):
                    story.append(Paragraph(f"<i>{stripped_line}</i>", styles['BodyTextCustom']))
                else:
                    story.append(Paragraph(stripped_line, styles['BodyTextCustom']))

            elif current_section == "SKILLS":
                if ':' in stripped_line:
                    parts = stripped_line.split(':', 1)
                    if len(parts) == 2:
                        story.append(Paragraph(f"<b>{parts[0].strip()}:</b> {parts[1].strip()}", styles['BodyTextCustom']))
                    else:
                        story.append(Paragraph(stripped_line, styles['BodyTextCustom']))
                else:
                    story.append(Paragraph(stripped_line, styles['BodyTextCustom']))

                if i < len(lines) - 1 and lines[i+1].strip() and lines[i+1].strip().lower() not in ["programming/technical", "tools & platforms", "concepts"]: # Adjusted condition
                   story.append(Spacer(1, 0.05 * inch))


            elif current_section == "PROJECTS":
                if stripped_line.startswith('*'):
                    story.append(Paragraph(stripped_line, styles['ListItem']))
                elif stripped_line.lower().startswith('**'):
                     story.append(Paragraph(stripped_line.replace('**', ''), styles['Heading2']))
                else:
                    story.append(Paragraph(stripped_line, styles['BodyTextCustom']))

            else:
                if not intro_block_processed:
                    story.append(Paragraph(stripped_line, styles['BodyTextCustom']))

        if story:
            story.append(Spacer(1, 0.2 * inch))


    else: # Logic for Cover Letter PDF generation (should be working fine)
        paragraphs = content_text.split('\n\n')
        for para in paragraphs:
            clean_para = para.strip()
            if clean_para:
                if clean_para.lower().startswith("dear"):
                    story.append(Paragraph(clean_para, styles['AddressLine']))
                    story.append(Spacer(1, 0.1 * inch))
                elif clean_para.lower().startswith("sincerely,") or clean_para.lower().startswith("best regards,"):
                    story.append(Paragraph(clean_para, styles['Signature']))
                    story.append(Spacer(1, 0.2 * inch))
                elif clean_para.strip().lower() == user_data['your_name'].lower():
                     story.append(Paragraph(clean_para, styles['Signature']))
                else:
                    story.append(Paragraph(clean_para, styles['BodyTextCustom']))
                    story.append(Spacer(1, 0.1 * inch))

    try:
        if not story:
            print(f"Warning: No content was parsed for '{filename}'. PDF will be blank or almost blank.")
            story.append(Paragraph("No content could be parsed for this document.", styles['BodyTextCustom']))
            story.append(Paragraph("Please check the raw AI output and adjust parsing logic in create_pdf.", styles['BodyTextCustom']))

        doc.build(story)
        return True
    except Exception as e:
        print(f"Error building PDF '{filename}': {e}")
        return False

# --- Main Execution Block ---

if __name__ == "__main__":
    user_details = get_user_input()

    if user_details:
        resume_text = generate_resume_content(user_details)
        cover_letter_text = generate_cover_letter_content(user_details)

        print("\n--- Generated Resume (Preview) ---")
        display(Markdown(resume_text))

        print("\n--- Generated Cover Letter (Preview) ---")
        display(Markdown(cover_letter_text))

        resume_name_part = "".join(c for c in user_details['your_name'] if c.isalnum() or c == ' ').replace(' ', '_')
        job_title_part = "".join(c for c in user_details['job_title'] if c.isalnum() or c == ' ').replace(' ', '_')

        resume_filename_pdf = f"{resume_name_part}_Resume_{job_title_part}.pdf"
        cover_letter_filename_pdf = f"{resume_name_part}_CoverLetter_{job_title_part}.pdf"

        print(f"\nAttempting to generate and download '{resume_filename_pdf}'...")
        if create_pdf(resume_filename_pdf, resume_text, user_details, title="Resume", is_cover_letter=False):
            try:
                files.download(resume_filename_pdf)
                print(f"'{resume_filename_pdf}' downloaded successfully!")
            except Exception as e:
                print(f"Error downloading resume PDF: {e}")
        else:
            print(f"Failed to create '{resume_filename_pdf}'.")

        print(f"\nAttempting to generate and download '{cover_letter_filename_pdf}'...")
        if create_pdf(cover_letter_filename_pdf, cover_letter_text, user_details, title="Cover Letter", is_cover_letter=True):
            try:
                files.download(cover_letter_filename_pdf)
                print(f"'{cover_letter_filename_pdf}' downloaded successfully!")
            except Exception as e:
                print(f"Error downloading cover letter PDF: {e}")
        else:
            print(f"Failed to create '{cover_letter_filename_pdf}'.")

        print("\nGeneration and download complete!")