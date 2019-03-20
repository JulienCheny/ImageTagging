"""
Ce programme défini une classe YoloAnnotationFilesGenerator utilisant pycocotools en python
"""

import sys, getopt, os
from pycocotools.coco import COCO

#imports des tests
import configparser

class YoloAnnotationFilesGenerator:
	"""
    Cette classe va génerer les fichiers d'annotations des objets de chaque image pour l'apprentissage du réseau de neurones Yolo
    """


	def convert(self, size, box):	# size : width, height, box : x, y, width, height
		"""
        Convertie les coordonnées d'une boite contenant un objet du format Coco (base d'images) vers le format Yolo (détecteur d'objets)

        :type size: Liste d'entiers
        :param size: taille de l'image (width, heigth)

        :type box: Liste d'entiers
        :param box: coordonnées de la boite au format Coco

        :return: coordonnées de la boite au format Yolo
        :rtype: Liste de décimales
        """

		dw = 1./size[0]
		dh = 1./size[1]
		cx = box[0] + box[1]/2.0
		cy = box[1] + box[3]/2.0
		cx = cx*dw
		cy = cy*dh
		w = box[2]*dw
		h = box[3]*dh
		return (cx,cy,w,h)

	def generateAnnotsYolofile(self, coco, labelFileFormat, selectedCatIds, labelsPath, datatype):  # datatype : (train or val) + date (2014 or 2017) ex : train2014
		"""
        Génère les fichiers d'annotations, necessaire à un apprentissage Yolo, d'une base coco spécifique et d'une selection d'objets spécifiques

        :type coco: objet Coco de la bibliothàque pycocotools
        :param coco: Parseur coco de fichier json contenant des annotations d'images

        :type labelFileFormat: String
        :param labelFileFormat: format des fichiers d'annotations générés

		:type selectedCatIds: Liste d'Entiers
        :param selectedCatIds: Les id des objets séléctionnés

        :type labelsPath: String
        :param labelsPath: chemin des fichiers annotations

        :type datatype: String
        :param datatype: nom du fichier annotation Coco parent

        :return: id des images contenant au moins un des objets séléctionnés
        :rtype: Liste d'Entiers
        """


		imgIds = coco.getImgIds()

		usedImgsId = []

		'''annotationsRepertory = labelsPath + "/" + datatype;

		try:
			os.mkdir(annotationsRepertory)
		except FileExistsError:
			print("directory already exists")'''

		for imgId in imgIds:

			file = None

			img = coco.loadImgs(imgId)[0]
			imgWidth = img['width']
			imgHeight = img['height']
			#print(str(imgWidth) + " " + str(imgHeight)) 

			#### Récupération de la liste d'annotations de l'image courante
			annIds = coco.getAnnIds(imgIds=imgId, iscrowd=None)
			anns = coco.loadAnns(annIds)
		
			#### Première boucle sur chaque annotation
			for ann in anns:
				catId = ann['category_id']
				#### Filtrage par la whitelist
				if catId in selectedCatIds:
					if file == None:
						formattedImgId = str(imgId).zfill(12)
						#print(labelsPath + '/' + datatype + '/' + labelFileFormat.format(datatype, formattedImgId))
						file = open(labelsPath + '/' + datatype + '/' + labelFileFormat.format(datatype, formattedImgId),"w+")
						usedImgsId.append(formattedImgId)
					bbox = ann['bbox']
					#print(bbox)
					yoloBbox = self.convert([img['width'], img['height']], bbox)
					#print(val)
					file.write(str(catId) + ' ' + ' '.join(str(e) for e in yoloBbox) + "\n")
			if file != None:
				file.close()
		return usedImgsId

	def writePartImgFile(self, datatype, metaFilePath, imgPathFormat, imgIds):
		"""
        Génère le meta-fichier, necessaire à un apprentissage Yolo, contenant le chemin des images utilisées pour l'apprentissage

        :type datatype: String
        :param datatype: nom du fichier annotation Coco parent

        :type metaFilePath: String
        :param metaFilePath: chemin du fichier meta à générer

		:type imgPathFormat: String
        :param imgPathFormat: format des fichiers d'images

        :type imgIds: Liste d'Entiers
        :param imgIds: id des images contenant au moins un des objets séléctionnés
        """

		partFile = open(metaFilePath,"a+")
		for imgId in imgIds:
			partFile.write(imgPathFormat.format(datatype, imgId) + "\n")
		partFile.close()



def test():
	config = configparser.ConfigParser()
	configFile = 'test/configs.conf'

	### recuperation des configurations
	config.read(configFile)

	catNm = "person"
	
	paramsGen = YoloAnnotationFilesGenerator()

	labelsPath = config['COCO']['labelDirectory'].format(catNm)

	# train
	partTrainFilePath = config['Yolo_arguments']['annFileFormat'].format(catNm, 'train')
	if os.path.exists(partTrainFilePath):
		os.remove(partTrainFilePath)

	for datatype in config['COCO']['trainFiles'].split(','):
		createDir(labelsPath + '/' + datatype)
		absolutePathAnnFile = config['COCO']['annFileFormat'].format(datatype)
		usedImgsId = paramsGen.generateAnnotsYolofile(COCO(absolutePathAnnFile), config['Yolo_arguments']['labelFileFormat'], sel.keepEdgeTabIds, labelsPath, datatype)

		paramsGen.writePartImgFile(datatype, partTrainFilePath, config['COCO']['imagesDirectory'] + '/' + datatype + '/' + config['Yolo_arguments']['imageFileFormat'], usedImgsId)