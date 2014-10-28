/**
 * Populate a graph with input nodes and links in the Graph JSON
 * @param inputJSONGraph, input JSON containing the edges and links for the graph
 * @param graph, dagreD3 Digraph graph object which is to be populated with nodes and edges from the input JSON
 * @param colorFunctionName, A parameter
 *
 */
function graphFromGraphJSONHighlightNode(inputJSONGraph, graph, colorFunctionName)
{
    var jsonNodesData;
    var jsonEdgesData;

    // Read the json data and store the nodes and the edges in a separate variable
    for (var key in inputJSONGraph)
    {
        if (inputJSONGraph.hasOwnProperty(key)) {
            if (key === "nodes") {
                jsonNodesData = inputJSONGraph[key];
            }
            if (key === "edges") {
                jsonEdgesData = inputJSONGraph[key];
            }
        }
    }

    addNodesToGraphHighlightNode(jsonNodesData, graph, colorFunctionName);
    addEdgesToGraph(jsonEdgesData, graph);
    return 0;
}

function graphFromGraphJSON(inputJSONGraph, graph)
{
    var jsonNodesData;
    var jsonEdgesData;

    // Read the json data and store the nodes and the edges in a separate variable
    for (var key in inputJSONGraph)
    {
        if (inputJSONGraph.hasOwnProperty(key)) {
            if (key === "nodes") {
                jsonNodesData = inputJSONGraph[key];
            }
            if (key === "edges") {
                jsonEdgesData = inputJSONGraph[key];
            }
        }
    }

    addNodesToGraph(jsonNodesData, graph);
    addEdgesToGraph(jsonEdgesData, graph);
    return 0;
}


function addNodesToGraph(nodesJSONArray, graphObj)
{

    for (var i = 0; i < nodesJSONArray.length; i++)
    {
        var nodeJSONObj = nodesJSONArray[i];
        graphObj.addNode(nodeJSONObj["id"], { label: nodeJSONObj["id"]});
    }
}

function addNodesToGraphHighlightNode(nodesJSONArray, graphObj, highlightNodeName)
{

    for (var i = 0; i < nodesJSONArray.length; i++)
    {
        var nodeJSONObj = nodesJSONArray[i];
        if (nodeJSONObj["id"] === highlightNodeName)
            graphObj.addNode(nodeJSONObj["id"], {label: nodeJSONObj["id"], style: "fill: red"});
        else
            graphObj.addNode(nodeJSONObj["id"], { label: nodeJSONObj["id"]});
    }
}

function addEdgesToGraph(edgesJSONArray, graphObj)
{

    for (var i = 0; i < edgesJSONArray.length; i++) {
        var edgeJSONObj = edgesJSONArray[i];
        graphObj.addEdge(null, edgeJSONObj["source"], edgeJSONObj["target"]);
    }
}


var graphHolderCopy;
var rightSecStyle;
var scriptsDiv;
var svg_g;

/* Global for storing graph paths */
var pathGraphs = [];

var main = function () {

    graphHolderCopy = $('#graphHolder').clone();
    scriptsDiv = $('#scripts').clone();
    rightSecStyle = $('#rightSecStyle').clone();
    svg_g = $('#svg_g').clone();

    console.log("print 2");

    $("#form1").submit(function (event) {

        /* Prevent the form from submitting normally */
        event.preventDefault();

        var $form = $(this);
        var url = $form.attr('action');

        /* Generate a post request with the file name in url */
        $.post(url, {apiName: "exploreFunction", functionName: $('#functionName').val(), subGraphDepthStr: $('#subGraphDepth').val()}, function(data, textStatus) {

            console.log("post success handler called");

            var graph = new dagreD3.Digraph();

            var responseJSONObj = data;

            if (responseJSONObj["success"] === "false") {
                $('#graphHolder').remove();
                $('#rightSec').text(jsonData['errorMessage']);
                return;
            }

            var jsonGraph = responseJSONObj["subGraphJSON"];

            /* Define nodes and edges variables */
            var jsonNodesData;
            var jsonEdgesData;

            graphFromGraphJSONHighlightNode(jsonGraph, graph, $('#functionName').val())

            var renderer = new dagreD3.Renderer();

            var layout = new dagreD3.layout()
                .rankDir("LR")

            //var svg = d3.select('g');

            var svg = d3.select('svg > g');
            svg.selectAll("*").remove();


            zoomG = svg.append('g');
            var zoom = dagreD3.zoom.panAndZoom(zoomG);

            dagreD3.zoom(svg, zoom);

            renderer.layout(layout).run(graph, zoomG);

        }, "json");

    })


    $("#form2").submit(function (event) {

        /* Prevent the form from submitting normally */
        event.preventDefault();

        var $form = $(this);
        var url = $form.attr('action');

        /* Generate a post request with the file name in url */
        $.post(url, {apiName: "getAllPathsSourceDestFuncs", sourceFuncName: $('#sourceFuncName').val(), destFuncName: $('#destFuncName').val()}, function(data, textStatus) {

            var graph = new dagreD3.Digraph();

            var responseJSONObj = data;

            if (responseJSONObj["success"] === "false") {
                console.log("call failed");
                return;
            }

            $("#resultsDiv").append();

            var pathGraphsResults = [];
            //var pathGraphs = [];

            for (i = 0; i < responseJSONObj["pathsJSON"].length; i++)
            {
                pathGraphsResults.push(responseJSONObj["pathsJSON"][i]);
                pathGraphs.push(new dagreD3.Digraph());
            }

            /* Convert each of the search results to a dagre Graph */
            for (i = 0; i < pathGraphsResults.length; i++)
            {
                returnStatus = graphFromGraphJSON(pathGraphsResults[i], pathGraphs[i]);
                if (returnStatus === -1) {
                    throw ("Could not create graph from result:" + i);
                }
            }

            rootSearchElement = document.getElementById('searchResultsDiv');

            /* Create Search Results */
            for (i = 0; i < pathGraphsResults.length; i++)
            {
                searchResultElement = document.createElement('div');
                searchResultElement.setAttribute("id", ("searchResultElement" + i));
                $('#searchResultsDiv').append(searchResultElement);
                $('#searchResultElement' + i).text("Path#:" + i);
                $('#searchResultElement' + i).data("pathNum", i);
                $('#searchResultElement' + i).click(function(event) {

                    pathNumValue = $('#' + event.target.id).data("pathNum");


                    /* Load the graph */
                    console.log(pathNumValue);

                    var graph1 = pathGraphs[pathNumValue];

                    var renderer = new dagreD3.Renderer();
                    var layout = new dagreD3.layout()
                        .rankDir("LR")

                    var svg = d3.select('svg > g');
                    svg.selectAll("*").remove();

                    zoomG = svg.append('g');
                    var zoom = dagreD3.zoom.panAndZoom(zoomG);

                    dagreD3.zoom(svg, zoom);

                    renderer.layout(layout).run(graph1, zoomG);

                });
            }
        });

    })
}

$(document).ready(main);
