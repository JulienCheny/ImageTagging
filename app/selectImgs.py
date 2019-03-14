import sys, getopt
import networkx as nx

class ImgsSelector(object):
    def __init__(self):
      self.mean = 0
      self.keepEdgeTabIds = []
      self.keepEdgeTabNames = []

    def getSumHistoTab(self, g, categoryId):
        sumTab = []

        for edge in g.edges(data=True):
            if edge[0] == str(categoryId):
                histo = edge[2]['object']
                sumEffect = sum(val for key, val in histo.items())

                sumTab.append([edge[1], sumEffect])
        return sumTab;

    def getKeepedEdges(self, g, mean, sumTab, percentFilter, printInfos):
        keepEdgeTab = []
        for edge in sumTab:
            percentSimilarity = round(edge[1]/mean*100,2)

            if percentSimilarity > percentFilter:
                keepEdgeTab.append(int(edge[0]))
            else:
                if printInfos:
                	print("forget node : " + str(g.node[edge[0]]['name']) + " (" + edge[0] + ") with " + str(percentSimilarity) + "%")
        return keepEdgeTab;

    def selectImgs(self, graphinputfile, categoryName, percentFilter, printInfos):
        ### Récupère le graphe
        g = nx.read_gml(graphinputfile)

        ### Converti le nom de categorie en id
        categoryId = int([x for x,y in g.nodes(data=True) if y['name']==categoryName][0])

        sumTab = self.getSumHistoTab(g, categoryId)

        self.mean = int(sum(n for _, n in sumTab) / len(sumTab))

        self.keepEdgeTabIds = self.getKeepedEdges(g, self.mean, sumTab, percentFilter, printInfos);

        self.keepEdgeTabNames = [g.node[str(x)]['name'] for x in self.keepEdgeTabIds];
        return self.keepEdgeTabIds

def main(argv):
    ### Récuperation des paramètres d'entrées
    graphinputfile = ''
    categoryName = ''
    percentFilter = 10
    try:
        opts, args = getopt.getopt(argv,"hg:c:f:",["ifile=","cname=","pfilter="])
    except getopt.GetoptError:
        print('opt error')
        print ('Command pattern : selectImgs.py -g <inputfile> -c <categoryName> -f <percentFilter>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('Command pattern : selectImgs.py -g <inputfile> -c <categoryName> -f <percentFilter>')
            sys.exit()
        elif opt in ("-g", "--ifile"):
            graphinputfile = arg
        elif opt in ("-c", "--cname"):
            categoryName = arg
        elif opt in ("-f", "--pfilter"):
            percentFilter = int(arg)

    sel = ImgsSelector()
    sel.selectImgs(graphinputfile, categoryName, percentFilter, True)

    print("result:")
    print(sel.mean)
    print(sel.keepEdgeTabIds)
    print(sel.keepEdgeTabNames)

if __name__ == "__main__":
   main(sys.argv[1:])