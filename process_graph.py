#!/usr/bin/python

import pdb
import networkx as nx
import hashlib
import argparse
import os
from networkx.readwrite import json_graph
import json
from random import randrange

class inputGraph:

    def __init__(self, name):
        self.name = name
        self.g = self.read_graph_file()
        self.g = self.pre_process_nodes(self.g)
        #self.g = self.hash_node_labels(self.g)
        self.g = self.relabel_nodes_to_function_names_hash(self.g)
        self.g = self.multigraph_to_graph(self.g)

    def read_graph_file(self):
        g = nx.read_dot(self.name)
        if g is None:
            print ("Failed to read graph file: %s" % self.name)
        return g

    #Go through the graph, remove any nodes that don't have a label property
    #Also remove any node with label "external node"
    def pre_process_nodes(self, g):

        #Here i will be a string like '1', '2', '3'
        #Here g.nodes_iter(data=True) is going to return a tuple like: ('1', {"name":xyz, "label":blah})
        #So element 0 of the tuple is the node identifier. and element 1 of the tuple contains
        #the node data.
        for i in g.nodes_iter(data=True):
            if "label" not in i[1]:
                #TODO: Print a more indicative error message to indicate which node is being removed
                print "Removing node: ", i[0]

                #See if more data is available about the node:
                if (len(i[1]) > 0):
                    print "Node details: "
                    for key in i[1]:
                        print i[1][key]
                g.remove_node(i[0])

        for i in g.nodes_iter(data=True):
            if i[1]["label"] == "{external node}":
                print "Removing node with external_node label: ", i[0]
                g.remove_node(i[0])
        return g

    #Go through the graph and convert the graph labels to be unique.
    #The disjoint union function combines two graphs by their labels, so
    #it is important that we use unique node labels.

    #When iterating through the graph, node_iter is returning each node as a tuple.
    #The first element of the tuple i.e. i[0] returns a "1" or "2" which is a str
    # and serves as the node id in our case. The second element of the tuple, i[1]
    # is the dictionary of data associated with this node.
    def hash_node_labels(self, g):
        for i in g.nodes_iter(data=True):
            m = hashlib.md5()
            m.update(i[1]["label"])
            i[1]["id"] = int(m.hexdigest(), 16)
        return g

    def relabel_nodes_to_function_names_hash(self, g):
        new_node_labels = {}
        for i in g.nodes_iter(data=True):
            new_node_labels[i[0]] = i[1]["label"]
        return nx.relabel_nodes(g, new_node_labels)



    #Convert multigraph to graph
    def multigraph_to_graph(self, g):
        print "Multigraph to digraph convert"
        modified_graph = nx.DiGraph()

        #Here 'edge' will be a tuple containing the 2 nodes between which this edge exists
        #So edge[0] will give first node and edge[1] will give the second node
        for edge in g.edges_iter():
            if not (modified_graph.has_edge(edge[0],edge[1])):
                if not (modified_graph.has_node(edge[0])):
                    modified_graph.add_node(edge[0])
                    modified_graph.node[edge[0]] = g.node[edge[0]]
                if not (modified_graph.add_node(edge[1])):
                    modified_graph.add_node(edge[1])
                    modified_graph.node[edge[1]] = g.node[edge[1]]
                modified_graph.add_edge(edge[0], edge[1])

        #Now add those nodes which may not have any edges and may have been left out


        return modified_graph


parser = argparse.ArgumentParser(description = "Combine dot file graphs")
parser.add_argument("-i", action="append", dest="input_graph", default=None, help="Input graph names", nargs="+", required=True)
parser.add_argument("-o", action="store", dest="output_graph", default="output.dot", help="Output graph name")

input_graph_file = parser.parse_args().input_graph[0]
output_graph_file = parser.parse_args().output_graph

input_graph_objs = []

for name in input_graph_file:
    input_graph_objs.append(inputGraph(name))

for i in input_graph_objs:
    nx.write_dot(i.g, i.name.replace(".dot", "_mod.dot"))

out_graph_obj = nx.DiGraph()

for i in input_graph_objs:
    out_graph_obj.add_nodes_from(i.g.nodes(data=True))
    out_graph_obj.add_edges_from(i.g.edges(data=True))

counter = 1
for edge in out_graph_obj.edges_iter(data=True):
    edge[2]["id"] = str(counter)
    counter = counter + 1
    edge[2]["source"] = edge[0]
    edge[2]["target"] = edge[1]

json_link_dict = {}
json_link_dict["id"] = "id"
json_link_dict["source"] = "source_numeric"
json_link_dict["target"] = "target_numeric"

#Temporary hack
x = 10
y = 10

for i in out_graph_obj.nodes_iter(data=True):
    i[1]["x"] = randrange(300)
    i[1]["y"] = randrange(300)



nx.write_dot(out_graph_obj, output_graph_file)

data = json_graph.node_link_data(out_graph_obj, json_link_dict)

f1 = open(output_graph_file.replace(".dot", ".json"), "w")
json.dump(data, f1)
f1.close()


print "done!"
exit(0)
