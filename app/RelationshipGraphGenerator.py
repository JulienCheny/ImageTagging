"""
Ce programme défini une classe RelationshipGraphGenerator utilisant Networkx et pycocotools en python
"""

import sys, getopt
from pycocotools.coco import COCO
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pylab
import math
import csv
import copy
import networkx as nx

pylab.rcParams['figure.figsize'] = (8.0, 10.0)
class RelationshipGraphGenerator:
	"""
	Cette classe va générer un graphe de relations spatiales depuis des fichiers d'annotations d'images
	"""

	def __init__(self, whitelistFile, annotationsPaths):
		"""
        Génère le graphe de relations spatiales

        :type whitelistFile: String
        :param whitelistFile: le chemin du fichier Whitelist
        
        :type annotationsPaths: String
        :param annotationsPaths:le chemin des fichiers d'annotations d'images
        """


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

		# Recupération du fichier des catégories whitelistées
		catNms = self.getWhitelistCsv(whitelistFile)
		
		# Recupération des id des categories whitelistées
		catWhiteIds = cocoParsers[0].getCatIds(catNms=catNms)

		# Création d'un tableau couplant les id et les noms des categories whitelistées
		catWhiteIdAndName = []
		for i in range(len(catWhiteIds)):
			catWhiteIdAndName.append([catWhiteIds[i],{'name': catNms[i]}])
		
		# Ajout des categories dans le graphe en temps que noeuds
		self.g.add_nodes_from(catWhiteIdAndName)
		

		# Remplissage du graphe en utilisant chaque parseur coco
		for coco in cocoParsers:
			self.fillGraph(catWhiteIds, coco)
	

	def getWhitelistCsv(self, filename):
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

	def saveGraph(self, graphfile):
		"""
        Sauvegarde le graphe dans un fichier

        :type graphfile: String
        :param graphfile: le chemin du fichier graphe (gml)
        """
		nx.write_gml(self.g, graphfile)

	def getGraph(self):
		"""
        Récupère le graphe

        :return: le graphe
		:rtype: objet DiGraph de la bibliothèque networkx
        """
		return self.g

	def graphAddValue(self,catIdX,catIdY, angleName):
		"""
        Ajoute une valeur au graphe. Ajoute un arc si il n'existe pas puis incrémente une valeur de l'arc

		:type catIdX: Entier
        :param catIdX: id de la categorie / noeud X

        :type catIdY: Entier
        :param catIdY: id de la categorie / noeud Y

        :type angleName: String
        :param angleName: nom de l'angle sur lequel la valeur a été incrémenté

        :return: l'histogramme des angles de l'arc
		:rtype: Objet
        """
		edgData = self.g.get_edge_data(catIdX, catIdY)
		if edgData is None:
			self.g.add_edge(catIdX,catIdY, object=copy.copy(self.emptyHisto))
		self.g[catIdX][catIdY]['object'][angleName] += 1

		return self.g[catIdX][catIdY]['object'];

	def getCenterOfSquare(self, bbox):
		"""
        Récupère le centre d'un rectangle donné

		:type bbox: Liste de décimales
        :param bbox: coordonnées du rectangle

        :return: coordonnées du point centre du rectangle
		:rtype: Liste de décimales
        """
		return [bbox[0] + bbox[2] / 2.0, bbox[1] + bbox[3]/2.0];

	def getAngleBetween(self, pos1, pos2):
		"""
        Calcul l'angle entre deux points

		:type pos1: Liste de décimales
        :param pos1: coordonnées du point 1

        :type pos2: Liste de décimales
        :param pos2: coordonnées du point 2

        :return: Valeur de l'angle entre les 2 points
		:rtype: Décimal
        """
		myradians = math.atan2(pos2[1]-pos1[1], pos2[0]-pos1[0])
		mydegrees = math.degrees(myradians)
		return round(mydegrees,1);

	def getAngleName(self, angle):
		"""
        Récupère le nom (orientation) d'un angle donné

		:type angle: Décimal
        :param angle: Valeur d'un angle entre les 2 points

        :return: Nom de l'angle
		:rtype: String
        """
		angleName = 'up';
		if angle < 45 and angle > - 45:
			angleName = 'left'
		if angle < - 45 and angle > - 135:
			angleName = 'down'
		if angle < - 135 or angle > 135:
			angleName = 'right'
		return angleName;

	def displayEdges(self):
		"""
        Affiche tous les arcs du graphe
        """

		for edgeData in self.g.edges(data=True):
			print(edgeData)

	def fillGraph(self, catWhiteIds, coco):
		"""
        Rempli le graphe avec les relations spatiales trouvés dans les annotations

		:type catWhiteIds: Liste d'Entiers
        :param catWhiteIds: Les id des objets whitelistés

        :type coco: objet Coco de la bibliothàque pycocotools
        :param coco: Parseur coco de fichier json contenant des annotations d'images
        """

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
