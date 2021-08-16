import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 		# suppress TF Warnings 
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'		# to fix some Apple Silicon known issues

from flask import Flask, flash, jsonify, request, redirect, url_for
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

from model.model import UNet
from model.data import EMData
from model.utils import Iterator, Images

# 
# Model
#

# dataset
DATASET_PATH = './data'
TEST_DATA_PATH = DATASET_PATH + '/test/img'
TRAIN_DATA_PATH = DATASET_PATH + '/train/img'
LABELS_DATA_PATH = DATASET_PATH + '/labels/img'

# input / output
COLOR_MODE = {'grayscale': 1, 'rgb': 3, 'rgba': 4} 		# no. of channels
IMG_COLOR_MODE = COLOR_MODE['grayscale']
IMG_W_H = (512, 512)									# pixels
INPUT_SHAPE = (IMG_W_H[0], IMG_W_H[1], IMG_COLOR_MODE)
OUTPUT_SHAPE = 1 										# binary matrices being predicted
# EPOCHS = 10
# STEPS_PER_EPOCH = 500
# VALIDATION_SPLIT = 0.2 # 20% of the traning data

# TODO
#init model

# 
# Flask
#
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# upload
ALLOWED_EXTENSIONS = set(['tiff', 'tif', 'jpg', 'jpeg', 'png'])
UPLOAD_FOLDER = './tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# utils
def _pack_response(data):
	if not data:
		data = {}

	response = jsonify(data)
	return response

def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# routes
@app.route('/', methods = ['GET'])
def upload_file():
	return "Helo"
		
@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/from_img', methods = ['POST'])
@cross_origin()
def predict_from_img():

	# check if the post request has the file part
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']

	# If the user does not select a file, the browser submits an
	# empty file without a filename.
	if file.filename == '':
		flash('No selected file')
		return redirect(request.url)

	if file and _allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		output = {'prediction': url_for('download_file', name=filename)}
		
		return _pack_response(output)

#
# Main
#
if __name__ == '__main__':
	app.run(debug=True)