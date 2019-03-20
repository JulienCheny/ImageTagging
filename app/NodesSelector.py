"""
Ce programme défini une classe NodesSelector utilisant Networkx en python
"""

import sys, getopt
import networkx as nx

class NodesSelector(object):
    """
    Cette classe va sélectionner depuis un noeud, les noeuds les plus pertinents par les relations spatiales
    """

    def __init__(self):
        """
        Défini les variables de la classe
        """
        self.keepEdgeTabIds = []
        self.keepEdgeTabNames = []

    def getSumHistoTab(self, g, categoryId):
        """
        Récupère la somme des effectifs dans chaque histogramme de chaque noeud

        :type g: objet DiGraoh de la classe networkx
        :param g: le graphe de relations spatiales

        :return: somme des effectifs  de chaque histogramme
        :rtype: Tableau 2D d'entiers (id du noeud + somme de l'histogramme)
        """

        sumTab = []

        for edge in g.edges(data=True):
            if edge[0] == str(categoryId):
                histo = edge[2]['object']
                sumEffect = sum(val for key, val in histo.items())

                sumTab.append([edge[1], sumEffect])
        return sumTab;

    def getKeepedEdges(self, g, mean, sumTab, percentFilter, printInfos):
        """
        Calcul les noeuds séléctionnés comme étant pertinents par les relations spatiales
        Garde les noeuds avec un effectif supérieur à un certain pourcentage (percentFilter) de la moyenne (mean)

        :type g: objet DiGraoh de la classe networkx
        :param g: le graphe de relations spatiales

        :type mean: Entier
        :param mean: moyenne des effectifs des histogrammes de tous les noeuds

        :type sumTab: Tableau 2D d'entiers (id du noeud + somme de l'histogramme)
        :param sumTab: somme des effectifs  de chaque histogramme

        :type percentFilter: Entier
        :param percentFilter: Pourcentage de selection par rapport à la moyenne

        :type printInfos: booléen
        :param printInfos: afficher ou non les informations

        :return: les ids des noeuds séléctionnés
        :rtype: Liste d'entiers
        """

        keepEdgeTab = []
        for edge in sumTab:
            percentSimilarity = round(edge[1]/mean*100,2)

            if percentSimilarity > percentFilter:
                keepEdgeTab.append(int(edge[0]))
            else:
                if printInfos:
                	print("forget node : " + str(g.node[edge[0]]['name']) + " (" + edge[0] + ") with " + str(percentSimilarity) + "%")
        return keepEdgeTab;

    def selectNodes(self, graphinputfile, categoryName, percentFilter, printInfos):
        """
        Rassemble les données necessaires puis récupère les noeuds séléctionnés

        :type graphinputfile: objet DiGraoh de la classe networkx
        :param graphinputfile: le graphe de relations spatiales

        :type categoryName: String
        :param categoryName: nom du noeud (categorie) sur lequel sélectionner les noeuds pertinents

        :type percentFilter: Entier
        :param percentFilter: Pourcentage de selection par rapport à la moyenne

        :type printInfos: booléen
        :param printInfos: afficher ou non les informations

        :return: les ids des noeuds séléctionnés
        :rtype: Liste d'entiers
        """

        ### Récupère le graphe
        g = nx.read_gml(graphinputfile)

        ### Converti le nom de categorie en id
        categoryId = int([x for x,y in g.nodes(data=True) if y['name']==categoryName][0])

        sumTab = self.getSumHistoTab(g, categoryId)

        mean = int(sum(n for _, n in sumTab) / len(sumTab))

        self.keepEdgeTabIds = self.getKeepedEdges(g, mean, sumTab, percentFilter, printInfos);

        self.keepEdgeTabNames = [g.node[str(x)]['name'] for x in self.keepEdgeTabIds];
        return self.keepEdgeTabIds


def test():
    ### Récuperation des paramètres d'entrées
    graphinputfile = 'graph_test.gml'
    categoryName = 'person'
    percentFilter = 10

    sel = NodesSelector()
    sel.selectNodes(graphinputfile, categoryName, percentFilter, True)

    print("Résultat :")
    print("Moyenne des effectifs : " + sel.mean)
    print("Id des objets séléctionnés : " + sel.keepEdgeTabIds)
    print("Noms des objets séléctionnés : " + sel.keepEdgeTabNames)


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