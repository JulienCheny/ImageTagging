import os, sys, getopt
from pycocotools.coco import COCO
import pylab, math, csv, copy, configparser
import networkx as nx

from networkxGenCoco import GraphGenerator
from selectImgs import ImgsSelector
from genYoloParameters import ParamsGenerator

config = configparser.ConfigParser()

def createDir(path):
	os.makedirs(path, exist_ok = True)

#def createCocoClassesNameFile(cocoClassesNameFileFormat, selectedClasses):
	

def createCfgCocoFile(cfgFilePath, classesCount, trainFilePath, validFilePath,classesNamePath, backupPath):
	cfgCocoFileContent = 'classes = {}\ntrain = {}\nvalid = {}\nnames = {}\nbackup = {}\neval = coco'


	cfgCocoFile = open(cfgFilePath,"w+")
	cfgCocoFile.write(cfgCocoFileContent.format(classesCount, trainFilePath, validFilePath,classesNamePath, backupPath))
	cfgCocoFile.close()


def getWhitelistCsv(filename):
		try:
			with open(filename, newline='') as csvfile:
				spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
				return [ item for innerlist in spamreader for item in innerlist ]
		except FileNotFoundError:
			print("whitelist file no found")
			return []

def main(argv):
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
	graphGen = GraphGenerator(whitelistFile, annValFilesTab)

	#graphGen.displayEdges()

	graphGen.saveGraph(config['Graph_generator_arguments']['graphFile'])


	### Selection des images
	sel = ImgsSelector()

	for catNm in catNms:
		sel.selectImgs(config['Graph_generator_arguments']['graphFile'], catNm, float(config['Network_image_selector']['percentFilter']), False)
		#print(sel.keepEdgeTabNames)



		### generation des params
		paramsGen = ParamsGenerator()

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
