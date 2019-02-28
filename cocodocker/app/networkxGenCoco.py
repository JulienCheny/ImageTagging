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

### Fichier json des annotations coco
annFile2014='../datas/annotations/instances_val2014.json'
annFile2017='../datas/annotations/instances_val2017.json'

### Histogramme vide d'un arc du graphe
emptyHisto = {
    "up": 0,
    "down": 0,
    "left": 0,
    "right": 0
}

def graphAddValue(g,catIdX,catIdY, angleName):

	edgData = g.get_edge_data(catIdX, catIdY)
	if edgData is None:
		g.add_edge(catIdX,catIdY, object=copy.copy(emptyHisto))
	g[catIdX][catIdY]['object'][angleName] += 1

	return g[catIdX][catIdY]['object'];

def getWhitelistCsv(filename):
	try:
		with open(filename, newline='') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
			return [ item for innerlist in spamreader for item in innerlist ]
	except FileNotFoundError:
		print("whitelist file no found")
		return []

def getCenterOfSquare(bbox):
	return [bbox[0] + bbox[2] / 2.0, bbox[1] + bbox[3]/2.0];

def getAngleBetween(pos1, pos2):
	myradians = math.atan2(pos2[1]-pos1[1], pos2[0]-pos1[0])
	mydegrees = math.degrees(myradians)
	return round(mydegrees,1);

def getAngleName(angle):
	angleName = 'up';
	if angle < 45 and angle > - 45:
		angleName = 'left'
	if angle < - 45 and angle > - 135:
		angleName = 'down'
	if angle < - 135 or angle > 135:
		angleName = 'right'
	return angleName;

def displayEdges(g):
	for edgeData in g.edges(data=True):
		print(edgeData)

def fillGraph(g, catWhiteIds, coco):

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
						angle = getAngleBetween(getCenterOfSquare(bboxTarget), getCenterOfSquare(bbox))
						angleName = getAngleName(angle)
						edg = graphAddValue(g, catId, catIdTarget, angleName)

def main(argv):
	### Récuperation des paramètres d'entrées
	graphOutputfile = 'graphresult.gml'
	whitelistFilename = 'whitelist.csv'
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


	### Initialisation du graphe
	g = nx.DiGraph()
	#nx.set_node_attributes(g,'', 'name');

	### Initialisation du parseur coco
	coco14=COCO(annFile2014)
	coco17=COCO(annFile2017)

	# Recupération des catégories whitelistées
	catNms = getWhitelistCsv(whitelistFilename)
	
	catWhiteIds = coco14.getCatIds(catNms=catNms)

	catWhiteIdAndName = []
	for i in range(len(catWhiteIds)):
		catWhiteIdAndName.append([catWhiteIds[i],{'name': catNms[i]}])
	
	g.add_nodes_from(catWhiteIdAndName)

	print(nx.get_node_attributes(g,'name'))
	
	fillGraph(g, catWhiteIds, coco14)
	fillGraph(g, catWhiteIds, coco17)
	
	displayEdges(g)
	nx.write_gml(g, graphOutputfile)

if __name__ == "__main__":
   main(sys.argv[1:])