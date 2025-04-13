import re
import docx
import pdfminer
from pdfminer.high_level import extract_text
import spacy
import nltk
from nltk.corpus import stopwords
from typing import Dict
from collections import Counter
import streamlit as st
from io import StringIO
import nltk
nltk.download('stopwords', quiet=True)

# Initialize NLP model
nlp = spacy.load("en_core_web_sm")

# Load stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Function to extract text from DOCX file
def extract_text_from_docx(file) -> str:
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Function to extract text from PDF file
def extract_text_from_pdf(file) -> str:
    text = extract_text(file)
    return text

# Function to extract name, email, skills, and experience using NLP
def extract_resume_info(text: str) -> Dict:
    doc = nlp(text)

    # Extract name (Assuming it is the first person mentioned in the document)
    name = ""
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    # Extract email
    email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
    email = email.group(0) if email else ""

    # Extract skills: Here we'll use a predefined list of skills or keywords
    skills_list = ["Python", "Java", "C", "JavaScript", "SQL", "Machine Learning", "Data Science", "Deep Learning", "Django", "React", "Flask", "AWS", "Azure", "NLP"]
    skills = [skill for skill in skills_list if skill.lower() in text.lower()]

    # Extract experience: Simple keyword-based experience detection
    experience_keywords = ["experience", "years", "worked as", "role"]
    experience = [sent.text for sent in doc.sents if any(keyword in sent.text.lower() for keyword in experience_keywords)]

    return {
        "name": name,
        "email": email,
        "skills": skills,
        "experience": experience
    }

# Function to highlight keywords in the resume based on the job description
def highlight_keywords(resume_text: str, job_description: str) -> Dict:
    # Tokenize the resume and job description
    resume_tokens = [token.text.lower() for token in nlp(resume_text) if token.text.lower() not in stop_words]
    job_tokens = [token.text.lower() for token in nlp(job_description) if token.text.lower() not in stop_words]

    # Count the frequency of each word in both resume and job description
    resume_counter = Counter(resume_tokens)
    job_counter = Counter(job_tokens)

    # Highlight matching keywords
    matching_keywords = [word for word in job_tokens if word in resume_counter]

    return {
        "matching_keywords": matching_keywords,
        "highlighted_resume": [word if word in matching_keywords else f"\033[1;31m{word}\033[0m" for word in resume_tokens]
    }

# Function to calculate match percentage based on skills in the job description and resume
def calculate_match_percentage(resume_skills: list, job_description_skills: list) -> float:
    common_skills = set(resume_skills).intersection(set(job_description_skills))
    total_skills = set(job_description_skills)
    
    match_percentage = (len(common_skills) / len(total_skills)) * 100 if total_skills else 0
    return round(match_percentage, 2)

# Streamlit UI
st.title("Resume Parser & Skill Extractor")

# Upload resume
uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

# Job description input
job_description = st.text_area("Enter Job Description", height=150)

if uploaded_file and job_description:
    # Step 1: Extract text from the uploaded resume
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        resume_text = extract_text_from_docx(uploaded_file)
    
    # Step 2: Extract resume information
    resume_info = extract_resume_info(resume_text)
    
    # Step 3: Highlight keywords in the resume based on the job description
    highlighted = highlight_keywords(resume_text, job_description)
    
    # Step 4: Calculate match percentage based on skills
    job_description_skills = ["Python", "Java", "C", "Machine Learning", "Data Science", "Deep Learning", "Django", "React", "AWS"]  # Example job description skills
    match_percentage = calculate_match_percentage(resume_info["skills"], job_description_skills)
    
    # Display Results
    st.subheader("Resume Information")
    st.write(f"Name: {resume_info['name']}")
    st.write(f"Email: {resume_info['email']}")
    st.write(f"Skills: {', '.join(resume_info['skills'])}")
    st.write(f"Experience: {', '.join(resume_info['experience'])}")
    
    st.subheader("Matching Keywords")
    st.write(", ".join(highlighted["matching_keywords"]))
    
    st.subheader("Highlighted Resume Text")
    st.text_area("Highlighted Resume", value=" ".join(highlighted["highlighted_resume"]), height=300)
    
    st.subheader("Match Percentage")
    st.write(f"Match Percentage: {match_percentage}%")

else:
    st.write("Upload a resume and provide a job description to start.")
