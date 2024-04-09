from django.shortcuts import render, redirect
from django.contrib import messages

import requests
from .custom_packages.initializeFirebase import initialize_firebase
from firebase_admin import storage

from nltk.tokenize import sent_tokenize
import re
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import uuid
import time
import os
initialize_firebase()

def home(request):
    if request.method == "POST":
        if 'file' in request.FILES:
            selected_option = request.POST.get('radio')
            number_of_mcq = request.POST['numberOfmcq']
            allowed_extensions = ['jpg', 'png', 'jpeg']
            uploaded_file = request.FILES['file']
            file_extension = uploaded_file.name.split('.')[-1]
            if int(number_of_mcq) >30:
                messages.warning(request, 'Max 30 mcqs generate at once!')
                return redirect('home') 
            if file_extension.lower() in allowed_extensions:
                text = ocr_image_to_text(uploaded_file, uploaded_file.name)['text']
                if text:
                    sentences = filter_text(text)
                    mcqs = generate_mcq(sentences, number_of_mcq, selected_option)
                    response = to_pdf(mcqs)
                    if response:
                        context = {
                            'url':response
                        }
                        return render(request,'download.html',context)
                    else:
                        messages.warning(request, 'Something went wrong!')
                        return redirect('home') 
                else:
                    messages.warning(request, 'Text is not readable')
                    return redirect('home') 
            else:
                messages.warning(request, 'Please upload a file in a valid format.')
                return redirect('home') 
    return render(request, 'index.html')

def ocr_image_to_text(uploaded_file, unique_filename):
    bucket = storage.bucket()
    blob = bucket.blob('images/' + unique_filename)
    uploaded_file.seek(0)
    blob.upload_from_file(uploaded_file)
    blob.make_public()
    public_url = blob.public_url

    url = "https://image-to-text9.p.rapidapi.com/ocr"
    querystring = {"url": public_url}
    headers = {
        "X-RapidAPI-Key": "8322b31bb5mshbdd66e0fc0cb6f0p15ff18jsn02d815947d83",
        "X-RapidAPI-Host": "image-to-text9.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    blob.delete()
    return response.json()

def filter_text(text):
    filtered_text = re.sub(r'[^a-zA-Z0-9\s\.\!\?]','', text)
    return extract_sentences(filtered_text)

def extract_sentences(text):
    sentences = sent_tokenize(text)
    return sentences

def generate_mcq(sentences, num_of_questions, difficulty):
    genai.configure(api_key="AIzaSyAPCT_Vh61cfoqnkkIULPtlae5tImZfPu8")

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f'Generate {num_of_questions} Mcqs (MCQ Difficulty is {difficulty}) based on this lists data {sentences} make sure to add options and do not add answer keys')

    return response.text

def to_pdf(mcqs):
    temp_dir = "./temp"
    os.makedirs(temp_dir, exist_ok=True)

    unique_filename = str(uuid.uuid4()) + ".pdf"
    filename = os.path.join(temp_dir, unique_filename)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []
    mcq_list = mcqs.split("**MCQ") 
    for i, mcq in enumerate(mcq_list[1:]):
        mcq = mcq.strip().split("\n")
        mcq_title = mcq[0].strip(":")
        mcq_body = mcq[1:]
        content.append(Paragraph(f"<strong>{mcq_title}</strong>", styles["Title"]))
        content.append(Spacer(1, 12))
        for line in mcq_body:
            content.append(Paragraph(line.strip(), styles["Normal"]))
        if i < len(mcq_list) - 2:  
            content.append(Spacer(1, 24))
    doc.build(content)
    bucket = storage.bucket()
    blob = bucket.blob('pdfs/' + unique_filename)
    blob.upload_from_filename(filename)
    blob.make_public()
    os.remove(filename)
    return blob.public_url

def download(request):
    return render(request,'download.html')