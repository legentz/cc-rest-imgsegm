import os, uuid
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 		# suppress TF Warnings 
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'		# to fix some Apple Silicon known issues

from flask import Flask, flash, jsonify, request, redirect, url_for
from flask_cors import CORS, cross_origin
from datetime import datetime
from model.model import UNet
from model.data import EMData
from model.utils import Iterator, Images

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

# init model
unet = UNet(INPUT_SHAPE, OUTPUT_SHAPE)

# restore weights
unet.load_weights('./model/weights/pre_trained.h5')

# 
# Flask
#
app = Flask(__name__)

# NOTE: We may not use this in production
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# upload config
ALLOWED_EXTENSIONS = set(['tiff', 'tif', 'jpg', 'jpeg', 'png'])
UPLOAD_FOLDER = './tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 
# Helpers functions
# 

# pack the response into a JSON to be delivered within the response
def _pack_response(data = None):
	if not data:
		data = {}

	response = jsonify(data)
	return response

# check if files extensions are allowed
def _allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# iterate through a generator over the images in the directory and predict
def _read_from_tmp_and_predict(dir_to_read, f_name2path = None):

	# load images from the tmp folder
	tmp_iterator = Iterator.imgs_from_folder(directory=dir_to_read, normalize=True, output_shape=(1, 512, 512, 1))

	# predict!
	preds = unet.predict(tmp_iterator, verbose=1)
	# Optionally, we can set a threshold to have both version of the data
	#preds, binary_preds = unet.predict(test_data, threshold=0.5, verbose=1)

	return preds

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
			uuid_name = str(uuid.uuid4()) + '.' + f.filename.rsplit('.')[-1]
			f_path = os.path.join(sub_tmp_dir, uuid_name)

			# save in a dict (mapping) to be used when predicting
			f_name2path[uuid_name] = f_path

			f.save(f_path)
	
	print('Upload complete... Prediction time')

	# iterate over the subfolder within tmp 
	preds = _read_from_tmp_and_predict(sub_tmp_dir)
	print('Predictions (no.', len(preds), ') with shape', preds.shape)

	saved_imgs = Images.save_as_imgs(os.path.join(sub_tmp_dir, "preds"), preds, list(f_name2path.keys()))
	print('Saved predictions as images')

	print('saved', saved_imgs)

	return _pack_response(saved_imgs)

# prediction from the JS magnifier 
# NOTE: need to deal with 512x512 images
# https://www.geeksforgeeks.org/python-pil-image-resize-method/
@app.route('/from_selection', methods = ['POST'])
@cross_origin()
def predict_from_selection():
	pass

#
# Main
#
if __name__ == '__main__':
	app.run(debug=True)