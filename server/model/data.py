from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image
import os, shutil
import numpy as np

'''
This class is merely a wrapper for EM-Segmentation dataset. It checks, unpacks and
sets everything up before feeding those data to the UNet model. It is clear that this
class is needed for being clear and less noisy in the Jupyter Notebook.
'''
class EMData():
	def __init__(self, data_path):

		# check whether path does exists
		assert os.path.exists(data_path)

		# dataset 
		self.data_path = data_path
		self.dataset_to_folders = {
			'train-volume.tif': 'train/img',
			'train-labels.tif': 'labels/img',
			'test-volume.tif': 'test/img'
		}

		# data iterators (generators)
		self.data_generator = None
		self.split_train_for_validation = False
	
	'''
	It makes sure that folders structure is set up correctly
	and it does not overwrite anything, unintentionally
	'''
	def _set_folders_up(self, overwrite=False):

		# prepare folders (labels, train, test)
		for f in self.dataset_to_folders.values():
			f_path = os.path.join(self.data_path, f)
			
			# delete folders if not empty and if overwrite is True
			if os.path.exists(f_path):

				# we care only about not empty folders
				if len(os.listdir(f_path)) > 0:

					# cannot overwrite folders (and their content)
					# if overwrite not requested by the user
					if not overwrite: raise Exception('One or all folders are not empty. Set option overwrite=True to solve this')
					
					# overwrite 
					shutil.rmtree(f_path, ignore_errors=True)
					os.makedirs(f_path)

			# folders do not exist. Need to create them
			else: os.makedirs(f_path)

	'''
	Unpack the original multi-frame .tif file
	'''
	def unpack(self, overwrite=False, save_as='.tif'):

		# Set folders structure up
		self._set_folders_up(overwrite=overwrite)

		# need to be sure that we have each part of the dataset 
		for name, folder in self.dataset_to_folders.items():
			name_path = os.path.join(self.data_path, name)
			folder_path = os.path.join(self.data_path, folder)

			# need to be sure that both .tif and output folder do exist
			# TODO: move this part outside
			# TODO: os.path.join should be computed once
			assert os.path.exists(folder_path), folder_path + ' does not exists'
			assert os.path.exists(name_path), name_path + ' does not exists'

			# open .tif stack
			tif_stack = Image.open(name_path)
			tif_stack.load()

			print("Extracting no. {} frames from {}".format(tif_stack.n_frames, name))

			# save each piece of the stack
			for frame in range(tif_stack.n_frames):
				tif_stack.seek(frame)

				# ex. 11[.ext]
				frame_name = str(frame) + (save_as if save_as.startswith('.') else '.' + save_as)
				tif_stack.save(os.path.join(folder_path, frame_name))
	
	'''
	A small hack to read data_generator internal configuration
	and know something about '_validation_split' value
	'''
	def _is_valid_split_set(self):
		if self.data_generator is None:
			return False
		return self.data_generator.__dict__['_validation_split'] > 0.

	'''
	It provides an infinite stream of augmented data
	'''
	def _generate_data(self, subset, binary_labels=False, **kwargs):
		kwargs_ = {
			**dict(
				subset=subset,
				shuffle=True if subset == 'training' else False,
				class_mode=None,
				color_mode='rgb',
				target_size=(256, 256),
				batch_size=1,
				seed=None,
			),
			**kwargs
		}

		# fix: to avoid directory overwriting (just in case it's provided from the user) 
		if 'directory' in kwargs_: del kwargs_['directory']

		# setting directories up
		directory_X = os.path.join(self.data_path, 'train')
		directory_y = os.path.join(self.data_path, 'labels')

		# generators
		X = self.data_generator.flow_from_directory(directory_X, **kwargs_)
		y = self.data_generator.flow_from_directory(directory_y, **kwargs_)

		# yeild data from both generators
		for X, y in zip(X, y):

			# transform labels to binary if requested
			if binary_labels:
				y = np.where(y < 0.5, 0, 1)

			yield X, y

	'''
	ImageDataGenerator generator which will handle train/validation data augmentation
	'''
	def init_data_generator(self, data_augmentation=dict()):
		self.data_generator = ImageDataGenerator(**data_augmentation)

		# inform user about validation split
		if self._is_valid_split_set():
			print('A subset will be used for validation purposes (' + str(data_augmentation['validation_split'] * 100) + '%)')

	'''
	Overloading of the _generate_data method. It generates
	the augmented training data  
	'''
	def generate_train(self, binary_labels=False, **kwargs):
		assert self.data_generator is not None, 'You need to call \'set_data_generator_up\' method'

		# if validation_split has not been provided, use data just for traning (no subsets)
		subset = 'training' if self._is_valid_split_set() else None

		# generate training data
		return self._generate_data(subset, binary_labels=binary_labels, **kwargs)

	'''
	Overloading of the _generate_data method
	It generates the augmented validation data (if needed)  
	'''
	def generate_valid(self, binary_labels=False, **kwargs):
		assert self._is_valid_split_set(), 'You should\'ve set \'validation_split\' in \'set_data_generator_up\' method. All the data were used for training purposes.'  

		# it generates validation data
		return self._generate_data('validation', binary_labels=binary_labels, **kwargs)

	'''
	INFO: We don't have the test labels
	Test data is used for the prediction phase
	'''
	def generate_test(self):
		raise('Sorry, not implemented. However, you could iterate over test data through Iterator.imgs_from_folder.')

