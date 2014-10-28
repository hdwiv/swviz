import networkx as nx
from networkx.readwrite import json_graph
import os
import json

# Given a graph path, convert that path into a graph and then into a json
def convertGraphPathDict(pathList):

    pathGraph = nx.DiGraph()

    for node in pathList:
        pathGraph.add_node(node)

    for (i, node) in enumerate(pathList):
        if ((i+1) == len(pathList)):
            break
        pathGraph.add_edge(pathList[i], pathList[i+1])

    #Add data to edges
    counter = 1
    for edge in pathGraph.edges_iter(data=True):
        edge[2]["id"] = str(counter)
        edge[2]["source"] = edge[0]
        edge[2]["target"] = edge[1]
        counter = counter + 1

    #Define the attributes dictionary used in generating json
    jsonLinkDict = {}
    jsonLinkDict["id"] = "id"
    jsonLinkDict["source"] = "source_numeric"
    jsonLinkDict["target"] = "target_numeric"

    graphJSONIntermediate = json_graph.node_link_data(pathGraph, jsonLinkDict)
    graphJSONIntermediate["edges"] = graphJSONIntermediate["links"]
    del graphJSONIntermediate["links"]
    del graphJSONIntermediate["graph"]

    return graphJSONIntermediate


class graphAnalyze:
    def __init__(self, name):
        self.fileName = name
        self.programGraph = self.loadProgramGraph()

    def loadProgramGraph(self):
        temp = nx.read_dot(self.fileName)

        if temp is None:
            print ("Failed to load program graph: " + self.fileName)

        #Because the default graph is multigraph and we want a digraph
        #convert to digraph
        programGraph = nx.DiGraph(temp)

        #Add source, destination data to edges so that generating json becomes easy, if you don't do this,
        #then generating JSON representation of the graph becomes a problem
        counter = 1
        for edge in programGraph.edges_iter(data=True):
            edge[2]["id"] = str(counter)
            edge[2]["source"] = edge[0]
            edge[2]["target"] = edge[1]

        return programGraph

    def getFullProgramMap(self):

        #TODO: Move the process of json generation to it's own function
        #so that we don't have to call it every single time

        #Define the attributes dictionary used in generating json
        json_link_dict = {}
        json_link_dict["id"] = "id"
        json_link_dict["source"] = "source_numeric"
        json_link_dict["target"] = "target_numeric"

        #Add data to edges
        counter = 1
        for edge in self.programGraph.edges_iter(data=True):
            edge[2]["id"] = str(counter)
            edge[2]["source"] = edge[0]
            edge[2]["target"] = edge[1]

        graphJSONIntermediate = json_graph.node_link_data(self.programGraph, json_link_dict)
        graphJSONIntermediate["edges"] = graphJSONIntermediate["links"]
        del graphJSONIntermediate["links"]
        del graphJSONIntermediate["graph"]
        return json.dumps(graphJSONIntermediate)

    def getAllPaths(self, funcName, degree):
        degreeList = []
        for i in self.programGraph.nodes_iter(data = True):
            degreeList.append((i[1]['label'], self.programGraph.in_degree(i[0])))
            if (i[1]["label"] == funcName):
                print "Got the node"
                print i[0]
        temp = sorted(degreeList, key=lambda functionName: functionName[1])
        for i in temp:
            print i
        return

    def getSubGraphAroundNode(self, funcName, subGraphdepth):
        try:

            returnObj = {}
            returnObj["success"] = "false"
            returnObj["subGraphJSON"] = {}


            for i in self.programGraph.nodes_iter(data=True):
                if ((i[1]["label"]) == funcName):
                    neighborhoodGraph = nx.ego_graph(self.programGraph, i[0], radius=subGraphdepth, undirected=True)

                    #Store the number of nodes and edges in the result graph
                    returnObj["numNodes"] = nx.number_of_nodes(neighborhoodGraph)
                    returnObj["numEdges"] = nx.number_of_edges(neighborhoodGraph)

                    # Define the JSON attr dictionary
                    jsonLinkDict = {}
                    jsonLinkDict["id"] = "id"
                    jsonLinkDict["source"] = "source_numeric"
                    jsonLinkDict["target"] = "target_numeric"

                    graphJSONIntermediate = json_graph.node_link_data(neighborhoodGraph, jsonLinkDict)
                    graphJSONIntermediate["edges"] = graphJSONIntermediate["links"]
                    del graphJSONIntermediate["links"]
                    del graphJSONIntermediate["graph"]

                    returnObj["success"] = "true"

                    #Use dict copy if you're going to modify this dictionary beyond this point
                    returnObj["subGraphJSON"] = graphJSONIntermediate


                    return json.dumps(returnObj)
            raise Exception("Function not found: " + funcName)

        except Exception as e:
            print e.message
            returnObj["subGraphJSON"] = []
            returnObj["success"] = "false"
            returnObj["errorMessage"] = e.message
            return json.dumps(returnObj)


    def getAllPathsBetweenNodes(self, sourceFuncName, destFuncName):
        try:
            sourceNode = None
            destNode = None

            pathSearchJSONReturnObj = {}
            pathSearchJSONReturnObj["pathsJSON"] = []
            pathSearchJSONReturnObj["success"] = "false"

            for i in self.programGraph.nodes_iter(data = True):
                if (i[1]["label"] == sourceFuncName):
                    sourceNode = i[0]
                elif (i[1]["label"] == destFuncName):
                    destNode = i[0]
            if ((sourceNode == None) or (destNode == None)):
                raise Exception("Input nodes not found")

            paths = nx.all_simple_paths(self.programGraph, source=sourceNode, target=destNode)
            pathList = list(paths)
            if (len(pathList) > 0):
                pathSearchJSONReturnObj["success"] = "true"

            for path in pathList:
                pathSearchJSONReturnObj["pathsJSON"].append(convertGraphPathDict(path))

            x = json.dumps(pathSearchJSONReturnObj)
            return json.dumps(pathSearchJSONReturnObj)

        except Exception as e:
            print e.message;
            pathSearchJSONReturnObj["pathsJSON"] = []
            pathSearchJSONReturnObj["success"] = "false"
            pathSearchJSONReturnObj["errorMessage"] = e.message
            return json.dumps(pathSearchJSONReturnObj)

