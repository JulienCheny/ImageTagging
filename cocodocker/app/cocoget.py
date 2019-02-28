from pycocotools.coco import COCO
import numpy as np
#import skimage.io as io
import matplotlib
import matplotlib.pyplot as plt
import pylab
import math
import csv
import copy
from graph_tool.all import *

pylab.rcParams['figure.figsize'] = (8.0, 10.0)

#catNms = ['person','dog','skateboard'];
#catNms = [];

whitelistFilename = 'whitelist.csv'

dataDir='../datas/'
dataType='val2017'
annFile='{}annotations/instances_{}.json'.format(dataDir,dataType)

emptyHisto = {
    "up": 0,
    "down": 0,
    "left": 0,
    "right": 0
}

g = Graph(directed=True)
histoProp = g.new_edge_property("object")

def getCatNameById(coco,catId):
	return coco.loadCats(ids=catId)[0]['name']

def graphAddValue(catIdX,catIdY, angleName):
	vx = g.vertex(catIdX)
	vy = g.vertex(catIdY)
	edg = g.edge(vx, vy)
	#if histoProp[edg] is None:
	if edg is None:
		edg = g.add_edge(vx,vy,add_missing=True)
		histoProp[edg] = copy.copy(emptyHisto)
	histoProp[edg][angleName] = histoProp[edg][angleName] + 1
	return edg;

def graphInitVertex(catIds):
	for catId in catIds:
		g.add_vertex(catId)

def getWhitelistCsv(filename):
	try:
		with open(filename, newline='') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
			return [ item for innerlist in spamreader for item in innerlist ]
	except FileNotFoundError:
		print("whitelist file no found")
		return []

def getCenterOfSquare(bbox):
	return [(bbox[0] - bbox[2])/2 + bbox[2], (bbox[1] - bbox[3])/2 + bbox[3]];

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

def displayAllEdges(coco):
	g.edge_properties["histo"] = histoProp
	for edge in g.get_edges():
		print(getCatNameById(coco,int(edge[0])), getCatNameById(coco,int(edge[1])))
		print(histoProp[edge])
	pos = sfdp_layout(g)
	graph_draw(g, pos, output_size=(800, 800), vertex_size=2, edge_pen_width=1.2, vcmap=matplotlib.cm.gist_heat_r, output="test.png")

coco=COCO(annFile)

# PRE-FILTRE des categories
catNms = getWhitelistCsv(whitelistFilename)
imgIds = []

if catNms == []:
	print("Load all categories")
	cats = coco.loadCats(coco.getCatIds())
	for cat in cats:
		catNms.append(cat['name'])
	imgIds = coco.getImgIds()
else:
	imgIds = coco.getImgIds(catIds=coco.getCatIds(catNms=catNms))

catIds = coco.getCatIds(catNms=catNms)
#graphInitVertex(catIds)

for imgId in imgIds:
	#### Récupération de la liste d'annotations de l'image courante
	annIds = coco.getAnnIds(imgIds=imgId, iscrowd=None)
	anns = coco.loadAnns(annIds)

	'''if len(anns) == 3:
		print(imgId)

	continue'''
	graphInitVertex(catIds)

	#### Première boucle sur chaque annotation
	for ann in anns:
		catId = ann['category_id']
		catNm = getCatNameById(coco, catId)
		
		#### Filtrage par la whitelist
		if catNm in catNms:
			#print('source object ' + catNm)
			bbox = ann['bbox']
			#print(getCenterOfSquare(bbox))

			#### Seconde boucle sur chaque annotation
			for anntarget in anns:
				catIdTarget = anntarget['category_id']
				catNmTarget = getCatNameById(coco, catIdTarget)
				
				#### anti egalité ET Filtrage par la whitelist
				if anntarget != ann and catNmTarget in catNms:
					bboxTarget = anntarget['bbox']
					#print('target object ' + catNmTarget)
					#print(getCenterOfSquare(bboxTarget))
					#print(getCenterOfSquare(bboxTarget))
					angle = getAngleBetween(getCenterOfSquare(bboxTarget), getCenterOfSquare(bbox))
					angleName = getAngleName(angle)
					print(catNm + " " + catNmTarget + " " + angleName)
					edg = graphAddValue(catId, catIdTarget, angleName)
					#print(getAngleName(angle))
	break
displayAllEdges(coco)

#nms=[ann['name'] for ann in anns]
#print('COCO annotations: \n{}\n'.format(' '.join(nms)))