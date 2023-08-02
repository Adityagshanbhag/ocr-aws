import boto3
from trp import Document
import json
import os

def aws_textract(abs_path):
    # Add Files
    s3client = boto3.client('s3')
    textract = boto3.client('textract')

    filename = os.path.basename(abs_path)

    res1 = s3client.upload_file(abs_path, 'ocr-bucket1', filename)
    s3BucketName = "ocr-bucket1"
    documentName = filename

    # Start the document analysis job
    response = textract.start_document_analysis(
        DocumentLocation={
            'S3Object': {
                'Bucket': s3BucketName,
                'Name': documentName
            }
        },
        FeatureTypes=["FORMS"]
    )
    job_id = response['JobId']
    # Wait for the job to complete
    response = textract.get_document_analysis(JobId=job_id)
    status = response['JobStatus']
    while status == 'IN_PROGRESS':
        response = textract.get_document_analysis(JobId=job_id)
        status = response['JobStatus']

    if status == 'SUCCEEDED':
        # Extraction completed successfully, retrieve the extracted data
        fields = {}
        doc = Document(response)
        for page in doc.pages:
            for field in page.form.fields:
                fields[str(field.key)] = str(field.value)

        # Convert key-value pairs to JSON
        json_response = json.dumps(fields, indent=4)
    else:
        # Extraction failed, handle the failure scenario
        return None

    # Delete Files
    res3 = s3client.delete_object(Bucket='ocr-bucket1', Key=filename)
    return json_response

