# marksheet_verification/views.py

from django.shortcuts import render
from .forms import DocumentForm
import os
from PIL import Image
import pytesseract
import PyPDF2
from django.conf import settings
import difflib


def safe_get(value):
    """Return the value if it's not None, otherwise return an empty string."""
    return value if value is not None else ""


def upload_marksheet(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document_file = request.FILES['document_file']
            document_path = os.path.join(settings.MEDIA_ROOT, document_file.name)

            # Save the uploaded file
            with open(document_path, 'wb+') as destination:
                for chunk in document_file.chunks():
                    destination.write(chunk)

            # Extract text from the document (Image or PDF)
            extracted_text = ""
            if document_file.name.endswith(('.jpg', '.png')):
                image = Image.open(document_path)
                extracted_text = pytesseract.image_to_string(image)
            elif document_file.name.endswith('.pdf'):
                extracted_text = extract_text_from_pdf(document_path)

            # Prepare verification results
            results = {}
            name = safe_get(form.cleaned_data['name'])
            roll_no = safe_get(form.cleaned_data['roll_no'])
            result = safe_get(form.cleaned_data['result'])
            application_no = safe_get(form.cleaned_data['application_no'])
            category = safe_get(form.cleaned_data['category'])
            mother_name = safe_get(form.cleaned_data['mother_name'])
            subject_group = safe_get(form.cleaned_data['subject_group'])

            # Debugging: Print extracted text and the values being checked
            print(f"Extracted Text: {extracted_text}")
            print(f"Name: {name}, Roll No: {roll_no}, Result: {result}, Application No: {application_no}")

            # Verification logic
            results['name_check'] = "Match" if name.lower() in extracted_text.lower() else "Does not match"
            results['roll_no_check'] = "Match" if roll_no.lower() in extracted_text.lower() else "Does not match"

            if form.cleaned_data['document_type'] == 'ssc':
                results['result_check'] = "Match" if result.lower() in extracted_text.lower() else "Does not match"
                # Suggest nearest match if result does not match
                if results['result_check'] == "Does not match":
                    closest_match = difflib.get_close_matches(result.lower(), extracted_text.lower().split(), n=1)
                    results['nearest_result'] = closest_match[0] if closest_match else "No suggestions available."

            elif form.cleaned_data['document_type'] == 'cet':
                results[
                    'application_no_check'] = "Match" if application_no.lower() in extracted_text.lower() else "Does not match"
                results['category_check'] = "Match" if category.lower() in extracted_text.lower() else "Does not match"
                results[
                    'mother_name_check'] = "Match" if mother_name.lower() in extracted_text.lower() else "Does not match"
                results[
                    'subject_group_check'] = "Match" if subject_group.lower() in extracted_text.lower() else "Does not match"

            return render(request, 'marksheet_verification/result.html', {
                'form': form,
                'results': results,
                'extracted_text': extracted_text
            })
    else:
        form = DocumentForm()

    return render(request, 'marksheet_verification/upload.html', {'form': form})


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
    return text
