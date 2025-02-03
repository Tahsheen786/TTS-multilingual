from flask import Flask, render_template, request, send_from_directory
from gtts import gTTS
import os
import uuid
from tempfile import NamedTemporaryFile

app = Flask(__name__)
UPLOAD_FOLDER = 'static/audio'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

@app.route('/')
def index():
    print("Rendering index page...")
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert_to_speech():
    text = request.form.get('text')
    language = request.form.get('language')

    if not text:
        return "Error: No text provided."

    # Use gTTS to convert text to speech
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Define the audio file path in the static/audio folder
        audio_file_name = "output.mp3"
        audio_file_path = os.path.join(UPLOAD_FOLDER, audio_file_name)

        # Save the speech to the audio file
        tts.save(audio_file_path)
        audio_html = f'<audio controls><source src="/static/audio/{audio_file_name}" type="audio/mp3">Your browser does not support the audio element.</audio>'

        return audio_html

    except Exception as e:
        return f"Error generating audio: {str(e)}"

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
