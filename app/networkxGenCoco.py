import sys, getopt
from pycocotools.coco import COCO
import numpy as np
#import skimage.io as io
import matplotlib
import matplotlib.pyplot as plt
import pylab
import math
import csv
import copy
import networkx as nx

pylab.rcParams['figure.figsize'] = (8.0, 10.0)
class GraphGenerator:

	def __init__(self, whitelistFile, annotationsPaths):
		### Histogramme vide d'un arc du graphe
		self.emptyHisto = {
		    "up": 0,
		    "down": 0,
		    "left": 0,
		    "right": 0
		}

		### Initialisation du graphe
		self.g = nx.DiGraph()

		### Initialisation des parseurs coco (un par fichier)
		cocoParsers = [COCO(annFile) for annFile in annotationsPaths]

		#print(cocoParsers)

		# Recupération des catégories whitelistées
		catNms = self.getWhitelistCsv(whitelistFile)

		#print(catNms)
		
		catWhiteIds = cocoParsers[0].getCatIds(catNms=catNms)

		catWhiteIdAndName = []
		for i in range(len(catWhiteIds)):
			catWhiteIdAndName.append([catWhiteIds[i],{'name': catNms[i]}])
		
		self.g.add_nodes_from(catWhiteIdAndName)

		#print(nx.get_node_attributes(self.g, 'name'))
		
		for coco in cocoParsers:
			self.fillGraph(catWhiteIds, coco)
	

	def getWhitelistCsv(self, filename):
		try:
			with open(filename, newline='') as csvfile:
				spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
				return [ item for innerlist in spamreader for item in innerlist ]
		except FileNotFoundError:
			print("whitelist file no found")
			return []

	def saveGraph(self, graphfile):
		nx.write_gml(self.g, graphfile)

	def getGraph(self):
		return self.g

	def graphAddValue(self,catIdX,catIdY, angleName):

		edgData = self.g.get_edge_data(catIdX, catIdY)
		if edgData is None:
			self.g.add_edge(catIdX,catIdY, object=copy.copy(self.emptyHisto))
		self.g[catIdX][catIdY]['object'][angleName] += 1

		return self.g[catIdX][catIdY]['object'];

	def getCenterOfSquare(self, bbox):
		return [bbox[0] + bbox[2] / 2.0, bbox[1] + bbox[3]/2.0];

	def getAngleBetween(self, pos1, pos2):
		myradians = math.atan2(pos2[1]-pos1[1], pos2[0]-pos1[0])
		mydegrees = math.degrees(myradians)
		return round(mydegrees,1);

	def getAngleName(self, angle):
		angleName = 'up';
		if angle < 45 and angle > - 45:
			angleName = 'left'
		if angle < - 45 and angle > - 135:
			angleName = 'down'
		if angle < - 135 or angle > 135:
			angleName = 'right'
		return angleName;

	def displayEdges(self):
		for edgeData in self.g.edges(data=True):
			print(edgeData)

	def fillGraph(self, catWhiteIds, coco):

		imgIds = coco.getImgIds()

		for imgId in imgIds:
			#### Récupération de la liste d'annotations de l'image courante
			annIds = coco.getAnnIds(imgIds=imgId, iscrowd=None)
			anns = coco.loadAnns(annIds)
		
			#### Première boucle sur chaque annotation
			for ann in anns:
				catId = ann['category_id']
				
				#### Filtrage par la whitelist
				if catId in catWhiteIds:
					bbox = ann['bbox']
					#### Seconde boucle sur chaque annotation
					for anntarget in anns:
						catIdTarget = anntarget['category_id']
						
						#### anti egalité ET Filtrage par la whitelist
						if anntarget != ann and catIdTarget in catWhiteIds:
							bboxTarget = anntarget['bbox']
							angle = self.getAngleBetween(self.getCenterOfSquare(bboxTarget), self.getCenterOfSquare(bbox))
							angleName = self.getAngleName(angle)
							edg = self.graphAddValue(catId, catIdTarget, angleName)

def main(argv):
	### Récuperation des paramètres d'entrées
	graphOutputfile = 'graphresult.gml'
	whitelistFilename = 'whitelist.csv'
	annFile = '/srv/datas/annotations/instances_val2014.json'
	try:
		opts, args = getopt.getopt(argv,"hw:g:",["wfile=","gfile="])
	except getopt.GetoptError:
		print('opt error')
		print ('Command pattern : selectImgs.py -w <whitelistfile> -g <graphfile>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('Command pattern : selectImgs.py -w <whitelistfile> -g <graphfile>')
			sys.exit()
		elif opt in ("-w", "--wfile"):
			whitelistFilename = arg
		elif opt in ("-g", "--gfile"):
			graphOutputfile = arg

	gen = GraphGenerator(whitelistFilename, [annFile])

	gen.displayEdges()
	gen.saveGraph(graphOutputfile)

if __name__ == "__main__":
   main(sys.argv[1:])
