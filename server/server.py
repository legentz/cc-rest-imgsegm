import os, uuid
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 		# suppress TF Warnings 
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'		# to fix some Apple Silicon known issues

from flask import Flask, flash, jsonify, request, redirect, url_for
from flask_cors import CORS, cross_origin
from datetime import datetime
from model.model import UNet
from model.data import EMData
from model.utils import Iterator, Images

import numpy as np

# 
# Model
#

# dataset
IMGS_TO_PREDICT = './tmp' # TODO: change dir

# input / output
COLOR_MODE = {'grayscale': 1, 'rgb': 3, 'rgba': 4} 		# no. of channels
IMG_COLOR_MODE = COLOR_MODE['grayscale']
IMG_W_H = (512, 512)									# pixels
INPUT_SHAPE = (IMG_W_H[0], IMG_W_H[1], IMG_COLOR_MODE)
OUTPUT_SHAPE = 1 										# binary matrices being predicted
MAT_FORMAT = '.mat'

# init model
unet = UNet(INPUT_SHAPE, OUTPUT_SHAPE)

# restore weights
unet.load_weights('./model/weights/pre_trained.h5')

# 
# Flask
#
app = Flask(__name__, static_folder='tmp')

# NOTE: We may not use this in production
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# upload config
PROTOCOL = "http"
HOST = "0.0.0.0"
PORT = "5000"
BASE_URL = PROTOCOL + "://" + HOST + ":" + PORT
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
UPLOAD_FOLDER = 'tmp'
EXPOSE_URLS_AS_ABSOLUTE = False

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 
# Helpers functions
# 

def _check_urls(data = None):
	if not data:
		data = {}

	for img_name, urls in data.items():
		if EXPOSE_URLS_AS_ABSOLUTE:
			data[img_name]['input'] = "file:///" + data[img_name]['input']
			data[img_name]['output'] = "file:///" + data[img_name]['output']
		else:
			data[img_name]['input'] = BASE_URL + "/" + UPLOAD_FOLDER + "/" + (data[img_name]['input'].split(UPLOAD_FOLDER)[1])
			data[img_name]['output'] = BASE_URL + "/" + UPLOAD_FOLDER + "/" + (data[img_name]['output'].split(UPLOAD_FOLDER)[1])
	
	return data

# pack the response into a JSON to be delivered within the response
def _pack_response(data = None):
	if not data:
		data = {}

	_data = _check_urls(data)

	response = jsonify(_data)
	return response

# check if files extensions are allowed
def _allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# iterate through a generator over the images in the directory and predict
def _read_from_tmp_and_predict(dir_to_read, f_name2path = None, is_mat = False, mat_normalized = False):

	# load images from the tmp folder
	if not is_mat:
		tmp_iterator = Iterator.imgs_from_folder(directory=dir_to_read, normalize=True, output_shape=(1, 512, 512, 1))
	
	else:
		tmp_iterator = Iterator.mat_from_folder(directory=dir_to_read, normalize=(not mat_normalized), output_shape=(1, 512, 512, 1))

	return unet.predict(tmp_iterator, verbose=1)

# create a new sub-folder (under tmp) to store each upload/prediction
def _create_tmp_subfolder():
	mydir = os.path.join(
		os.getcwd(),
		UPLOAD_FOLDER, 
		datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
	
	try:
		os.makedirs(mydir)								# this folder have timestamp
		os.makedirs(os.path.join(mydir, 'preds')) 		# this folder will host predictions related to a single upload session
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise  # This was not a "directory exist" error..

	return mydir

# 
# Flask routes
#

# statically serve files
# NOTE: this is not suggested in production for a matter of security
# NOTE: disable directory listing
# @app.route('/preds/<name>')
# def download_file(path, name):
# 	return send_from_directory(path, name)

# upload one ore more images (locally), using uuid for file names,
# predict and serve results
# NOTE: replace local upload with Amazon S3 to store and serve images 
# https://www.zabana.me/notes/flask-tutorial-upload-files-amazon-s3
@app.route('/from_img', methods = ['POST'])
@cross_origin()
def predict_from_img():

	# handle more than one file
	n_files = len(request.files)
	print("Request to upload", n_files, "files")

	if n_files == 0: flash('No files provided')

	# TODO: create tmp subfolder with timestamp (so we can restore sorting?)
	sub_tmp_dir = _create_tmp_subfolder()
	f_name2path = {}
	print('Creating temp sub-folder', sub_tmp_dir)

	# iterate over each file
	for f_name in request.files:
		f = request.files[f_name]

		# check if it has an allowed extension
		if f and _allowed_file(f.filename):

			# replacing the name with an UUID to avoid dealing with strange names...
			uuid_name = str(uuid.uuid4())
			uuid_name_ext = str(uuid.uuid4()) + '.' + f.filename.rsplit('.')[-1]
			f_path = os.path.join(sub_tmp_dir, uuid_name_ext)

			# save in a dict (mapping) to be used when predicting
			f_name2path[uuid_name] = {'input': f_path, 'output': ''}

			f.save(f_path)
	
	print('Upload complete... Prediction time')

	# iterate over the subfolder within tmp 
	preds = _read_from_tmp_and_predict(sub_tmp_dir)
	print('Predictions (no.', len(preds), ') with shape', preds.shape)

	saved_imgs = Images.save_as_imgs(os.path.join(sub_tmp_dir, "preds"), preds, f_name2path)
	print('Saved predictions as images', saved_imgs)

	return _pack_response(saved_imgs)

# prediction from the JS magnifier 
# NOTE: need to deal with 512x512 images
# https://www.geeksforgeeks.org/python-pil-image-resize-method/
@app.route('/from_mat', methods = ['POST'])
@cross_origin()
def predict_from_mat():

	if request.json: # TODO: check normalized and images to be present
		is_norm = bool(request.json['normalized'])
		
		# TODO: create tmp subfolder with timestamp (so we can restore sorting?)
		sub_tmp_dir = _create_tmp_subfolder()
		f_name2path = {}
		print('Creating temp sub-folder', sub_tmp_dir)

		for mat in request.json['images']:
			mat_arr = np.asarray(mat, dtype=np.uint8)

			# replacing the name with an UUID to avoid dealing with strange names...
			uuid_name = str(uuid.uuid4())
			uuid_name_ext = str(uuid.uuid4()) + MAT_FORMAT
			f_path = os.path.join(sub_tmp_dir, uuid_name_ext)

			# save in a dict (mapping) to be used when predicting
			f_name2path[uuid_name] = {'input': f_path, 'output': ''}

			np.savetxt(f_path, mat_arr, fmt='%d')
	
	print('Created and saved .mat(s)... Prediction time')

	# iterate over the subfolder within tmp 
	preds = _read_from_tmp_and_predict(sub_tmp_dir, is_mat=True)
	print('Predictions (no.', len(preds), ') with shape', preds.shape)

	saved_imgs = Images.save_as_imgs(os.path.join(sub_tmp_dir, "preds"), preds, f_name2path)
	print('Saved predictions as images', saved_imgs)

	return _pack_response(saved_imgs)

#
# Main
#
if __name__ == '__main__':
	app.run(debug=True, port=PORT, host=HOST)

