from confapp import conf
import cv2, numpy as np, os
import base64

class ColorPropertiesDataset(object):

	def __init__(self, name=None):
		super(ColorPropertiesDataset, self).__init__(name)
		self._avg_colors = []
		self._avg_gray   = []
		
	######################################################################
	### EVENTS ###########################################################
	######################################################################

	def create_contoursimages_tree_nodes(self):
		self.create_group_node('color average', icon=conf.ANNOTATOR_ICON_COLORS)		
		self.create_data_node('color average > red', 	icon=conf.ANNOTATOR_ICON_COLOR_COMPONENT)
		self.create_data_node('color average > green',icon=conf.ANNOTATOR_ICON_COLOR_COMPONENT)
		self.create_data_node('color average > blue', icon=conf.ANNOTATOR_ICON_COLOR_COMPONENT)
		self.create_data_node('color average > gray', icon=conf.ANNOTATOR_ICON_COLOR_COMPONENT)
		
	######################################################################
	### FUNCTIONS ########################################################
	######################################################################

	################# CONTOUR #########################################################

	def get_coloraverage_red_value(self, index):
		color = self.get_color_avg(index)
		return None if color is None else color[0]
		
	def get_coloraverage_green_value(self, index):
		color = self.get_color_avg(index)
		return None if color is None else color[1]

	def get_coloraverage_blue_value(self, index):
		color = self.get_color_avg(index)
		return None if color is None else color[2]

	def get_coloraverage_gray_value(self, index):
		color = self.get_color_avg(index)
		return None if color is None else color[2]


	######################################################################
	### DATA ACCESS FUNCTIONS ############################################
	######################################################################

	def get_gray_avg(self, index):
		if index<0 or index>=len(self._avg_gray): return None
		return self._avg_gray[index] if self._avg_gray[index] is not None else None

	def set_gray_avg(self, index, color):
		if not hasattr(self, 'treenode_coloraverage'): self.create_contoursimages_tree_nodes()
		# add colors in case they do not exists
		if index >= len(self._avg_gray):
			for i in range(len(self._avg_gray), index + 1): self._avg_gray.append(None)
		self._avg_gray[index] = color

	def get_color_avg(self, index):
		if index<0 or index>=len(self._avg_colors): return None
		return self._avg_colors[index] if self._avg_colors[index] is not None else None

	def set_color_avg(self, index, color):
		if not hasattr(self, 'treenode_coloraverage'): self.create_contoursimages_tree_nodes()
		# add colors in case they do not exists
		if index >= len(self._avg_colors):
			for i in range(len(self._avg_colors), index + 1): self._avg_colors.append(None)

		color = color if color is not None and color[0] is not None and color[1] is not None and color[2] is not None else None		
		self._avg_colors[index] = color

	@property
	def has_colors_avg(self):
		return len(self._avg_colors)>0 or len(self._avg_gray)>0


	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################


	def save(self, data, datasets_path=None):
		data = super(ColorPropertiesDataset, self).save(data, datasets_path)
		dataset_path = self.directory

		colors_file = os.path.join(dataset_path, 'colors-average.csv')
		with open(colors_file, 'wb') as outfile:
			outfile.write((';'.join(['frame','red','green', 'blue', 'gray'])+'\n' ).encode( ))
			for index in range(len(self)):
				color = self.get_color_avg(index)
				gray = self.get_gray_avg(index)
				row = [index] + ([None, None, None] if color is None else list(color)) + [gray]
				outfile.write((';'.join( map(str,row) )).encode( ))
				outfile.write(b'\n')

		return data

	def load(self, data, dataset_path=None):
		super(ColorPropertiesDataset, self).load(data, dataset_path)
		colors_file = os.path.join(dataset_path, 'colors-average.csv')
		
		if os.path.exists(colors_file):
			with open(colors_file, 'r') as infile:
				infile.readline()
				for i, line in enumerate(infile):
					csvrow = line[:-1].split(';')
					
					frame 	= int(csvrow[0])
					red 	= float(csvrow[1]) if csvrow[1] is not None and csvrow[1]!='None' else None
					green 	= float(csvrow[2]) if csvrow[2] is not None and csvrow[2]!='None' else None
					blue 	= float(csvrow[3]) if csvrow[3] is not None and csvrow[3]!='None' else None
					gray 	= float(csvrow[4]) if csvrow[4] is not None and csvrow[4]!='None' else None

					color = (red,green,blue) if red is not None and blue is not None and green is not None else None
					self.set_color_avg(frame, color)

					self.set_gray_avg(frame, gray)