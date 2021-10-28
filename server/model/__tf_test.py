# suppress TF Warnings 
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

from model import UNet
from data import EMData
from utils import Iterator

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

emdata = EMData(data_path=DATASET_PATH)

# NOTE: if data is already in place, we mush use overwrite=True
emdata.unpack(save_as='.png', overwrite=True)


# init model
unet = UNet(INPUT_SHAPE, OUTPUT_SHAPE)

# show a summary of our model
unet.summary()

# to save weights
#unet_k.save_weights('./my_weights.h5')

# to restore weights from any checkpoint folder (last will be loaded)
#unet.load_weights('./checkpoints', checkpoint=True)

# to restore weights single file
unet.load_weights('./data/pre_trained/pre_trained.h5')

# load Test images from folder...
test_data = Iterator.imgs_from_folder(directory=TEST_DATA_PATH, normalize=True, output_shape=(1, 512, 512, 1))

# ... and predict!
preds = unet.predict(test_data, verbose=2)

# Optionally, we can set a threshold to have both version of the data
#preds, binary_preds = unet.predict(test_data, threshold=0.5, verbose=1)

print(preds)