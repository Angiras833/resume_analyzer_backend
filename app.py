from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from utils import analyze_resume

# Configuration
UPLOAD_FOLDER = '../uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_resume():
    file = request.files.get('resume')
    city = request.form.get('city')

    # Check for missing file or wrong file type
    if not file or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file. Only PDF or DOCX allowed.'})

    if not city:
        return jsonify({'success': False, 'message': 'City name is required.'})

    # Save the uploaded file securely
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Analyze the resume
    result = analyze_resume(filepath, city)

    # Check for errors from utils.py
    if isinstance(result, dict) and 'error' in result:
        return jsonify({'success': False, 'message': result['error']})

    # Return success response
    return jsonify({'success': True, 'data': result})

if __name__ == '__main__':
    app.run(debug=True)
