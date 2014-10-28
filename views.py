from django.shortcuts import render
from django.views.generic import View

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

import json
import graphAnalyzer

#Load the full graph over here
analyzerObj = graphAnalyzer.graphAnalyze("program.dot")

def exploreFunction(apiArgs):

    errorObj = {}
    errorObj["success"] = "false"
    errorObj["errorMessage"] = "Error Occurred"

    if (('functionName' not in apiArgs) or ('subGraphDepthStr' not in apiArgs)):
        errorObj["errorMessage"] = "Missing arguments in exploreFunction"
        return HttpResponse(json.dumps(errorObj), content_type="application/json")
    else:
        functionName = apiArgs['functionName']
        subGraphDepthStr = apiArgs['subGraphDepthStr']
        subGraphDepth = int(subGraphDepthStr)
        if ((functionName is not None) and (subGraphDepth is not None)):
            subGraphJSON = analyzerObj.getSubGraphAroundNode(functionName, subGraphDepth)
            return HttpResponse(subGraphJSON, content_type="application/json")
        else:
            errorObj["errorMessage"] = "Invalid arguments to exploreFunction"
            return HttpResponse(json.dumps(errorObj), content_type="application/json")

def getAllPathsSourceDestFuncs(apiArgs):
    errorObj = {}
    errorObj["success"] = "false"
    errorObj["errorMessage"] = "Missing arguments in getAllPathsSourceDestFuncs"
    if (('sourceFuncName' not in apiArgs) or ('destFuncName' not in apiArgs)):
        return HttpResponse(json.dumps(errorObj), content_type="application/json")
    else:
        sourceFuncName = apiArgs['sourceFuncName']
        destFuncName = apiArgs['destFuncName']
        searchPathsObj = analyzerObj.getAllPathsBetweenNodes(sourceFuncName, destFuncName)
        return HttpResponse(searchPathsObj, content_type="application/json")

availableAPIFuncs = {"exploreFunction": [exploreFunction, {"functionName": None, "subGraphDepthStr": None}],
                     "getAllPathsSourceDestFuncs": [getAllPathsSourceDestFuncs, {"sourceFuncName": None, "destFuncName": None}]}

@csrf_exempt
def index(request):

    if (request.method == 'GET'):
        return HttpResponse('Got called from analyzer with a GET request')
    elif (request.method == 'POST'):
        if 'apiName' in request.POST:
            apiName = request.POST['apiName']
            if apiName in availableAPIFuncs:
                for x in availableAPIFuncs[apiName][1]:
                    if x not in request.POST:
                        return HttpResponse("Malformed POST API request, missing api argument: " + x)
                    availableAPIFuncs[apiName][1][x] = request.POST[x]
                return availableAPIFuncs[apiName][0](availableAPIFuncs[apiName][1])
            else:
                return HttpResponse('Invalid API Name sent')
        else:
            return HttpResponse('Invalid POST request')
    return HttpResponse(x, content_type="application/json")
