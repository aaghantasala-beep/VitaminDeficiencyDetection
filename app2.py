from flask import Flask, render_template, request, current_app
import os
from werkzeug.utils import secure_filename
import label_image
import image_fuzzy_clustering as fem
from PIL import Image

app = Flask(__name__)
model = None

# Define the upload folder path
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'img')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route to home page
@app.route('/')
@app.route('/first')
def first():
    return render_template('first.html')

# Route to login page
@app.route('/login')
def login():
    return render_template('login.html')

# Route to chart page
@app.route('/chart')
def chart():
    return render_template('chart.html')

# Route to upload page
@app.route('/upload')
def upload():
    return render_template('index1.html')

# Route to success page after processing an image
@app.route('/success', methods=['POST'])
def success():
    if 'file' not in request.files or request.files['file'].filename == '':
        return "No file selected for uploading", 400

    i = request.form.get('cluster')
    f = request.files['file']

    try:
        # Save uploaded image
        original_pic_path = save_img(f, f.filename)

        # Process image with fuzzy clustering
        fem.plot_cluster_img(original_pic_path, i)

    except Exception as e:
        return f"Error processing the image: {str(e)}", 500

    return render_template('success.html')

def save_img(img, filename):
    directory = os.path.join(current_app.root_path, 'static', 'images')
    os.makedirs(directory, exist_ok=True)
    picture_path = os.path.join(directory, secure_filename(filename))

    try:
        # Ensure we are working with the correct file format
        img.seek(0)
        with Image.open(img) as i:
            i = i.convert("RGB")  # Ensure RGB format
            output_size = (300, 300)
            i.thumbnail(output_size)
            i.save(picture_path, format="JPEG")  # Save as JPEG to avoid file descriptor issues
    except Exception as e:
        raise Exception(f"Error saving image: {e}")

    return picture_path


# Route to index page
@app.route('/index')
def index():
    return render_template('index.html')

# Route to handle predictions
@app.route('/predict', methods=['GET', 'POST'])
def upload1():
    if request.method == 'POST':
        f = request.files.get('file')
        if not f:
            return "No file uploaded", 400

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        f.save(file_path)

        try:
            result = load_image(file_path)
            result = result.title()
        except Exception as e:
            return f"Error processing the file: {str(e)}", 500

        d = {
            "Vitamin A": " → Deficiency of vitamin A is associated with significant morbidity and mortality from common childhood infections, and is the world's leading preventable cause of childhood blindness. Vitamin A deficiency also contributes to maternal mortality and other poor outcomes of pregnancy and lactation.",
            "Vitamin B": " → Vitamin B12 deficiency may lead to a reduction in healthy red blood cells (anaemia). The nervous system may also be affected. Diet or certain medical conditions may be the cause. Symptoms are rare but can include fatigue, breathlessness, numbness, poor balance and memory trouble. Treatment includes dietary changes, B12 shots or supplements.",
            "Vitamin C": " → A condition caused by a severe lack of vitamin C in the diet. Vitamin C is found in citrus fruits and vegetables. Scurvy results from a deficiency of vitamin C in the diet. Symptoms may not occur for a few months after a person's dietary intake of vitamin C drops too low. Bruising, bleeding gums, weakness, fatigue and rash are among scurvy symptoms. Treatment involves taking vitamin C supplements and eating citrus fruits, potatoes, broccoli and strawberries.",
            "Vitamin D": " → Vitamin D deficiency can lead to a loss of bone density, which can contribute to osteoporosis and fractures (broken bones). Severe vitamin D deficiency can also lead to other diseases. In children, it can cause rickets. Rickets is a rare disease that causes the bones to become soft and bend.",
            "Vitamin E": " → Vitamin E needs some fat for the digestive system to absorb it. Vitamin E deficiency can cause nerve and muscle damage that results in loss of feeling in the arms and legs, loss of body movement control, muscle weakness, and vision problems. Another sign of deficiency is a weakened immune system."
        }

        result = result + d.get(result, "No additional information available")
        os.remove(file_path)
        return result

    return None

# Function to load and predict image label
def load_image(image):
    text = label_image.main(image)
    return text

if __name__ == '__main__':
    app.run(debug=True)
