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
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# upload config
ALLOWED_EXTENSIONS = set(['tiff', 'tif', 'jpg', 'jpeg', 'png'])
UPLOAD_FOLDER = './tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# utils
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

def _read_from_tmp_and_predict(dir_to_read, f_name2path = None):

	# load images from the tmp folder
	tmp_iterator = Iterator.imgs_from_folder(directory=dir_to_read, normalize=True, output_shape=(1, 512, 512, 1))

	# predict!
	preds = unet.predict(tmp_iterator, verbose=1)
	# Optionally, we can set a threshold to have both version of the data
	#preds, binary_preds = unet.predict(test_data, threshold=0.5, verbose=1)

	return preds

# create a new sub-folder to handle each upload/prediction
def _create_tmp_subfolder():
	mydir = os.path.join(
		os.getcwd(),
		UPLOAD_FOLDER, 
		datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
	
	try:
		os.makedirs(mydir)
		os.makedirs(os.path.join(mydir, 'preds'))
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise  # This was not a "directory exist" error..

	return mydir

# routes		
@app.route('/preds/<name>')
def download_file(path, name):
	return send_from_directory(path, name)

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

	# iterate over files
	for f_name in request.files:
		f = request.files[f_name]

		# check if it's allowed
		if f and _allowed_file(f.filename):

			# replacing the name with an UUID
			uuid_name = str(uuid.uuid4()) + '.' + f.filename.rsplit('.')[-1]
			f_path = os.path.join(sub_tmp_dir, uuid_name)

			# save in a dict to be used when predicting
			f_name2path[uuid_name] = f_path

			f.save(f_path)
			print('Upload complete... Prediction time')

	# TODO: directory listing with all updates and purge button
	#preds = {'prediction': url_for('download_file', name=filename)}

	# iterate over sub_tep_dir (restore sorting)
	preds = _read_from_tmp_and_predict(sub_tmp_dir)
	print('Predictions (no.', len(preds), ') with shape', preds.shape)

	print('Saving predictions as images')
	saved_imgs = Images.save_as_imgs(os.path.join(sub_tmp_dir, "preds"), preds, list(f_name2path.keys()))

	print('saved', saved_imgs)

	return _pack_response(saved_imgs)

#
# Main
#
if __name__ == '__main__':
	app.run(debug=True)