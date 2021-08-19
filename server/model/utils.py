# TODO: better imports... more specific
import os, re
import numpy as np 
import matplotlib.pyplot as plt
from matplotlib import cm
from sys import exc_info
from math import ceil
from PIL import Image, ImageOps

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

			print("Providing image", img)

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

			# img to ndarray
			# img = np.asarray(img)
			print('debug mat', img.shape)

			# normalize data 
			if normalize: img = img / img.max()

			# if output_shape, reshape!
			if output_shape is not None:
				img = img.reshape(output_shape)

			print("Providing image", img)

			yield(img)

'''
This class contains simple utilities concerning images visualization
within the Notebook of the project.
'''
class Images(object):

	'''
	This method plots a ndarray of images along n_rows/n_cols (as sub-plot)
	'''
	@staticmethod
	def plot_arr_to_imgs(arr, n_max=-1, cols=1, cmap=None, figsize=(15, 15)):
		n_imgs = len(arr)			# how many images
		rows = ceil(n_imgs / cols)	# how many rows

		# set figure size
		fig = plt.figure(figsize=figsize)

		for i in range(0, cols * rows):

			# load n_max images
			if i >= n_max: break

			# set a sub-plot for inline visualization
			fig.add_subplot(rows, cols, i + 1)

			# get the image depending on the input shape
			# ex. (10, 512, 512, 1) -> 10 512x512 images on 1 channel
			if len(arr.shape) == 4:
				img = arr[i, :, :, 0]

			elif len(arr.shape) == 3:
				img = arr[:, :, i]

			# we can assume it's width and height
			elif len(arr.shape) == 2:
				img = arr

			else: raise('Bad shaped array provided!')

			# add image to grid
			plt.imshow(img, cmap=cmap)

		# show
		plt.show()

	'''
	This method is almost a duplicate of the Iterator a ndarray of images along n_rows/n_cols (as sub-plot)
	'''
	@staticmethod
	def plot_imgs_from_folder(path, n_max=-1, cols=1, cmap=None, figsize=(15, 15)):
		assert os.path.exists(path)

		# we need to sort to be sure the order is maintained
		# our files are always 0.png, 1.png, ...
		# TODO: handle labels instead of sorting
		imgs = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
		imgs.sort()
		n_imgs = len(imgs) 
		rows = ceil(n_imgs / cols) 

		# set figure size
		fig = plt.figure(figsize=figsize)

		# loop over images number
		for i in range(0, n_imgs):

			# load n_max images
			if i >= n_max: break

			fig.add_subplot(rows, cols, i + 1)

			# TODO: make this a standalone function under Images utils
			try:
				img = Image.open(os.path.join(path, imgs[i]))
			except:
				print('WARNING:', exc_info()[0])
				continue

			# img to ndarray
			img = np.asarray(img)

			# add image to grid
			plt.imshow(img, cmap=cmap)

		# show
		plt.show()

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
			print("arr_im", arr_im.shape, arr_im)
			im = Image.fromarray(arr_im, mode='L')
			# im = Image.fromarray(np.uint8(arr.reshape(preds.shape[1], preds.shape[2])) * 255)

			print('image values before saving', im)

			im_path = os.path.join(output_dir, f_name_ext)
			im.save(im_path)

			f_name2path[f_name]['output'] = im_path

		return f_name2path




