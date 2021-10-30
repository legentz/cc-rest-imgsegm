# TODO: better imports... more specific
import os, re
import numpy as np 
from sys import exc_info
from math import ceil
from PIL import Image

'''
This class shall contain only simple/dummy generators (...maybe Iterator isn't the right name)
'''
class Iterator(object):

	'''
	This methods simply generates a flow of one image at a time
	taken from a specific folder. Used to quickly load a bunch of images in the Notebook.  
	'''
	@staticmethod
	# TODO: batched data
	def imgs_from_folder(directory=None, normalize=False, output_shape=None):
		assert os.path.exists(directory)

		# # we need to sort to be sure the order is maintained
		list_dir = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
		list_dir.sort()

		# loop over images in dir
		for img in list_dir:

			# TODO: make this a standalone function under Images utils
			try:
				img = Image.open(os.path.join(directory, img)).convert('L')

			except:
				print('WARNING:', exc_info()[0])
				continue

			# img to ndarray
			img = np.asarray(img)

			# normalize data 
			if normalize: img = img / img.max()

			# if output_shape, reshape!
			if output_shape is not None:
				img = img.reshape(output_shape)

			yield(img)

	'''
	This methods simply generates a flow of one .mat file at a time
	taken from a specific folder. Used to quickly load a bunch of images (as matrices) in the Notebook.  
	'''
	@staticmethod
	# TODO: batched data
	def mat_from_folder(directory=None, normalize=False, output_shape=None):
		assert os.path.exists(directory)

		# # we need to sort to be sure the order is maintained
		# NOTE: Do we need to check for .mat only?
		list_dir = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
		list_dir.sort()

		print('Iterating over .mat only', list_dir)

		# loop over images in dir
		for mat in list_dir:

			try:
				img = np.loadtxt(os.path.join(directory, mat), dtype=np.uint8)

			except:
				print('WARNING:', exc_info()[0])
				continue

			# normalize data 
			if normalize: img = img / img.max()

			# if output_shape, reshape!
			if output_shape is not None:
				img = img.reshape(output_shape)

			yield(img)

'''
This class contains simple utilities concerning images visualization
within the Notebook of the project.
'''
class Images(object):

	@staticmethod
	def save_as_imgs(output_dir, preds, f_name2path, use_format='.png'):
		assert output_dir is not None
		assert len(f_name2path.keys()) == preds.shape[0]

		# saved_imgs = []
		f_names = list(f_name2path.keys())
		
		# for each prediction of the shape(1, x, x, 1)
		for i in range(preds.shape[0]):
			arr, f_name = preds[i], f_names[i]

			# output format
			f_name_ext = f_name + use_format

			# reshape and save
			arr_im = np.uint8(arr.reshape((preds.shape[1], preds.shape[2])) * 255)
			print("arr_im", arr_im.shape)
			
			im = Image.fromarray(arr_im, mode='L')
			print('image values before saving', im)

			im_path = os.path.join(output_dir, f_name_ext)
			im.save(im_path)

			f_name2path[f_name]['output'] = im_path

		return f_name2path
