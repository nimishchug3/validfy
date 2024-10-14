from django import forms

class DocumentForm(forms.Form):
    document_type = forms.ChoiceField(
        choices=[
            ('ssc', 'SSC Marksheet'),
            ('cet', 'CET Marksheet'),
        ],
        required=True,
    )
    document_file = forms.FileField(required=True)

    # SSC Fields
    name = forms.CharField(required=False)
    roll_no = forms.CharField(required=False)
    result = forms.ChoiceField(choices=[('pass', 'Pass'), ('fail', 'Fail')], required=False)

    # CET Fields
    application_no = forms.CharField(required=False)
    cet_roll_no = forms.CharField(required=False)
    category = forms.CharField(required=False)
    mother_name = forms.CharField(required=False)
    subject_group = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get('document_type')

        # Clear non-applicable fields based on document type
        if document_type == 'ssc':
            cleaned_data['application_no'] = None
            cleaned_data['cet_roll_no'] = None
            cleaned_data['category'] = None
            cleaned_data['mother_name'] = None
            cleaned_data['subject_group'] = None
        elif document_type == 'cet':
            cleaned_data['name'] = None
            cleaned_data['roll_no'] = None
            cleaned_data['result'] = None

        return cleaned_data
