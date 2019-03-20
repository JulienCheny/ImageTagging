"""
Ce programme défini une commande utilisant les classes RelationshipGraphGenerator, NodesSelector et YoloAnnotationFilesGenerator ainsi que la librairie networkx et pycocotools en python
"""

import os, sys, getopt
from pycocotools.coco import COCO
import pylab, math, csv, copy, configparser
import networkx as nx

from RelationshipGraphGenerator import RelationshipGraphGenerator
from NodesSelector import NodesSelector
from YoloAnnotationFilesGenerator import YoloAnnotationFilesGenerator

config = configparser.ConfigParser()



def createDir(path):
	"""
    Créer un dossier au chemin indiqué

	:type path: String
    :param path: chemin du dossier
    """
	os.makedirs(path, exist_ok = True)

def createCfgCocoFile(cfgFilePath, classesCount, trainFilePath, validFilePath,classesNamePath, backupPath):
	"""
    Génère un fichier config yolo au chemin indiqué

	:type cfgFilePath: String
    :param cfgFilePath: chemin du fichier config

    :type classesCount: String
    :param classesCount: nombre de classes ( = noeuds = categories = objets)

    :type trainFilePath: String
    :param trainFilePath: chemin du metafichier des images d'apprentissages

    :type validFilePath: String
    :param validFilePath: chemin du metafichier des images de validations

    :type classesNamePath: String
    :param classesNamePath: chemin du fichier contenant le nom des classes

    :type backupPath: String
    :param backupPath: chemin du répertoire dans lequel enregistrer le résultat
    """

	cfgCocoFileContent = 'classes = {}\ntrain = {}\nvalid = {}\nnames = {}\nbackup = {}\neval = coco'


	cfgCocoFile = open(cfgFilePath,"w+")
	cfgCocoFile.write(cfgCocoFileContent.format(classesCount, trainFilePath, validFilePath,classesNamePath, backupPath))
	cfgCocoFile.close()


def getWhitelistCsv(filename):
	"""
    Récupère la whiteliste du fichier csv

    :type filename: String
    :param filename: le chemin du fichier whitelist

    :return: les noms d'objets contenu dans le fichier whitelist
	:rtype: liste de strings
    """

		try:
			with open(filename, newline='') as csvfile:
				spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
				return [ item for innerlist in spamreader for item in innerlist ]
		except FileNotFoundError:
			print("whitelist file no found")
			return []

def main(argv):
	"""
    Génère les fichiers de cofiguration de tous les réseaux de neurones à apprendre

    :type configfile: String
    :param configfile: le chemin du fichier de configuration du projet
    """


	### Récuperation des paramètres d'entrées
	configFile = 'configs.conf'
	try:
		opts, args = getopt.getopt(argv,"hc:",["wfile=","cfgfile="])
	except getopt.GetoptError:
		print('opt error')
		print ('Command pattern : GenNetworksParams.py -c <configfile>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('Command pattern : GenNetworksParams.py -c <configfile>')
			sys.exit()
		elif opt in ("-c", "--cfgfile"):
			configFile = arg

	### recuperation des configurations
	config.read(configFile)

	### recuperations des fichiers d'annotations
	annTrainFilesTab = [config['COCO']['annFileFormat'].format(annfile) for annfile in config['COCO']['trainFiles'].split(',')]
	annValFilesTab = [config['COCO']['annFileFormat'].format(annfile) for annfile in config['COCO']['valFiles'].split(',')]

	#print(annTrainFilesTab)
	#print(annValFilesTab)

	### recuperations des objets whitelistés
	whitelistFile = config['Graph_generator_arguments']['whitelistFile']
	catNms = getWhitelistCsv(whitelistFile)


	### Génération du graphe
	graphGen = RelationshipGraphGenerator(whitelistFile, annValFilesTab)

	#graphGen.displayEdges()

	graphGen.saveGraph(config['Graph_generator_arguments']['graphFile'])


	### Selection des images
	sel = NodesSelector()

	for catNm in catNms:
		sel.selectNodes(config['Graph_generator_arguments']['graphFile'], catNm, float(config['Network_image_selector']['percentFilter']), False)
		#print(sel.keepEdgeTabNames)



		### generation des params
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


		# val
		partValFilePath = config['Yolo_arguments']['annFileFormat'].format(catNm, 'val')
		if os.path.exists(partValFilePath):
			os.remove(partValFilePath)

		for datatype in config['COCO']['valFiles'].split(','):
			createDir(labelsPath + '/' + datatype)
			absolutePathAnnFile = config['COCO']['annFileFormat'].format(datatype)
			usedImgsId = paramsGen.generateAnnotsYolofile(COCO(absolutePathAnnFile), config['Yolo_arguments']['labelFileFormat'], sel.keepEdgeTabIds, labelsPath, datatype)

			paramsGen.writePartImgFile(datatype, partValFilePath, config['COCO']['imagesDirectory'] + '/' + datatype + '/' + config['Yolo_arguments']['imageFileFormat'], usedImgsId)


		createCfgCocoFile(
			config['Yolo_arguments']['cfgFile'].format(catNm, catNm),
			config['Darknet']['defaultClassesCount'],
			partTrainFilePath,
			partValFilePath,
			config['Darknet']['defaultClassesNameFile'],
			config['COCO']['backupDirectory'])
		
		#cfgFilePath, classesCount, trainFilePath, validFilePath,classesNamePath, backupPath

if __name__ == "__main__":
   main(sys.argv[1:])
