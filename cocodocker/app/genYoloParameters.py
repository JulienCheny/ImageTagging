import sys, getopt, os
from pycocotools.coco import COCO

from selectImgs import ImgsSelector


### Fichier json des annotations coco
fileNameVal2014 = "val2014"
fileNameTrain2014 = "train2014"

annFilePath = ('../datas/annotations/instances_', '.json')

imgFilePath = "/images/{}/COCO_{}_{}.jpg"
labelFilePath = "/labels/{}/COCO_{}_{}.txt"
### Initialisation du parseur coco  
coco=COCO(fileNameVal2014.join(annFilePath))
#coco17=COCO(annFile2017)

def convert(size, box):	# size : width, height, box : x, y, width, height
	dw = 1./size[0]
	dh = 1./size[1]
	cx = box[0] + box[1]/2.0
	cy = box[1] + box[3]/2.0
	cx = cx*dw
	cy = cy*dh
	w = box[2]*dw
	h = box[3]*dh
	return (cx,cy,w,h)

def generateAnnotsYolofile(selectedCatIds, coco, dataName):
	imgIds = coco.getImgIds()

	usedImgsId = []

	annotationsRepertory = os.getcwd() + "/labels/" + dataName;

	try:
		os.mkdir(annotationsRepertory)
	except FileExistsError:
		print("val2014 directory already exists")

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
					file = open(labelFilePath.format(dataName, dataName, formattedImgId),"w+")
					usedImgsId.append(formattedImgId)
				bbox = ann['bbox']
				#print(bbox)
				yoloBbox = convert([img['width'], img['height']], bbox)
				#print(val)
				file.write(str(catId) + ' ' + ' '.join(str(e) for e in yoloBbox) + "\n")
		if file != None:
			file.close()
	return usedImgsId

def writePartImgFile(fileName, filePathFormat, imgIds):
	partFile = open(fileName + ".part","w+")
	for imgId in imgIds:
		partFile.write(filePathFormat.format(fileName, fileName, imgId) + "\n")
	partFile.close()

try:
	os.mkdir(os.getcwd() + "/labels")
except FileExistsError:
	print("labels directory already exists")

sel = ImgsSelector()
sel.selectImgs("graph.gml", "car", 10, False)

usedImgsId = generateAnnotsYolofile(sel.keepEdgeTabIds, coco, fileNameVal2014)

writePartImgFile(fileNameVal2014, imgFilePath, usedImgsId)

'''b = (float(xmin), float(xmax), float(ymin), float(ymax))
bb = convert((w,h), b)
print(bb)'''
