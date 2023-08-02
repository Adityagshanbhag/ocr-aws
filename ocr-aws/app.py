from flask import Flask, render_template, request, redirect, url_for, Response
import os,io
import ocr
import zipfile
from werkzeug.utils import secure_filename

app = Flask(__name__)

var_list=[]

@app.route('/',methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        a=[]
        for f in request.files.getlist('file_name'):
            file_path = os.path.abspath(secure_filename(f.filename))
            a.append(file_path)
            var_list.append(a)
        return redirect(url_for('generate'))
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    a = var_list.pop()
    if len(a) == 1:
        json_data = ocr.aws_textract(a[0])
        # Set the response headers
        filename = os.path.basename(os.path.splitext(a[0])[0]) + '.json'
        response = Response(json_data, content_type='application/json')
        response.headers.set('Content-Disposition', 'attachment', filename=filename)
        return response

    if len(a) > 1:
        zip_filename = 'json_files.zip'
        zip_data = io.BytesIO()
        try:
            with zipfile.ZipFile(zip_data, 'w') as zipf:
                # Iterate over each file location and generate JSON data
                for file_location in a:
                    json_data = ocr.aws_textract(file_location)
                    filename = os.path.basename(file_location)  # Original filename without path
                    json_filename = os.path.splitext(filename)[0] + '.json'  # New filename with ".json" extension

                    # Add the JSON data to the zip file
                    zipf.writestr(json_filename, json_data)

            # Set the response headers for the zip file
            response = Response(zip_data.getvalue(), content_type='application/zip')
            response.headers.set('Content-Disposition', 'attachment', filename=zip_filename)
            return response
        finally:
            # Close the in-memory byte stream
            zip_data.close()

    return redirect(url_for('download'))



@app.route('/download',methods=['GET','POST'])
def download():
    return render_template('gen.html')

if __name__ == '__main__':
    app.run(debug=True)
