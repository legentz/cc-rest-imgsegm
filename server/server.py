from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

# suppress TF Warnings 
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

from model.model import UNet
from model.data import EMData
from model.utils import Iterator, Images

# dataset
DATASET_PATH = './data'
TEST_DATA_PATH = DATASET_PATH + '/test/img'
TRAIN_DATA_PATH = DATASET_PATH + '/train/img'
LABELS_DATA_PATH = DATASET_PATH + '/labels/img'

# input
COLOR_MODE = {'grayscale': 1, 'rgb': 3, 'rgba': 4} # channels
IMG_COLOR_MODE = COLOR_MODE['grayscale']
IMG_W_H = (512, 512)
INPUT_SHAPE = (IMG_W_H[0], IMG_W_H[1], IMG_COLOR_MODE)

# output
OUTPUT_SHAPE = 1
EPOCHS = 10
STEPS_PER_EPOCH = 500
VALIDATION_SPLIT = 0.2 # 20% of the traning data

# Flask
app = Flask(__name__)
api = Api(app)

# TODO
# init model

# argument parsing
parser = reqparse.RequestParser()
parser.add_argument("q")

class Prediction(Resource):
	def get(self):
		# use parser and find the user's query
		args = parser.parse_args()
		user_query = args['q']

		# predict

		prediction = "hardcoded"

		# create JSON object
		output = {'prediction': prediction}
		
		return output

api.add_resource(Prediction, '/')

if __name__ == '__main__':
	app.run(debug=True)