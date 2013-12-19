#-------------------------------------------------------------------------------
# Name:        BuildVectorPyramids
# Purpose:      Build vector pyramids for an input Feature Class
#
# Author:      Jeremy Moore
#
# Created:     01/09/2012
# Copyright:   (c) MN DNR 2012
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import os, sys, string, math, urllib
import pprint
from xml.etree import ElementTree
import arcpy, xml.dom.minidom
from xml.dom.minidom import Node
import xml.dom.minidom as minidom
from arcpy import env
import arcpy.management as DM
import arcpy.cartography as CA

arcpy.env.overwriteOutput = True;

# Class Functions
def printMessage(message):
    print message
    arcpy.AddMessage(message)

    # Conversion to get tolerance distance for simplifying
    # Assumes units in m and resolution of 300 dpi
def getTolerance(number):
    x = int(number)
    return int(((x/300)/12)*.305)

def getDefaultLODS(layerXML):
    defaultLODS = []
    for node in layerXML.getElementsByTagName("levels"):
        for scaleObj in node.getElementsByTagName("level"):
            lod = scaleObj.getAttribute("scale")
            defaultLODS.append(lod)
    return defaultLODS

def getOutputGDB(layerXML):
    for lyrs in layerXML.getElementsByTagName("layers"):
        for lyr in lyrs.getElementsByTagName("layer"):
            inFC = str(lyr.getAttribute("path"))
            outDBName =  os.path.dirname(inFC)
            return outDBName

def getLayerInfo(i):
    layerInfo ={}
    for lyrs in layerXML.getElementsByTagName("layers"):
        lyr= (lyrs.getElementsByTagName("layer")[i])

        for level in lyr.getElementsByTagName("level"):
            lod = level.getAttribute("scale")
            query = level.getAttribute("query")
            layerInfo[lod]= query
    if len(layerInfo) > 0:
        return layerInfo
    else:
        layerInfo = getDefaultLODS(layerXML)
        return layerInfo


def startSimplify():
     for lyrs in layerXML.getElementsByTagName("layers"):
        for i in range(len(lyrs.getElementsByTagName("layer"))):
            lyr= (lyrs.getElementsByTagName("layer")[i])
            inFC = str(lyr.getAttribute("path"))
            print "inFC: "+inFC
            lyrInfo = getLayerInfo(i)
            print "Layer Info: "+ str(lyrInfo)
            gdb = getOutputGDB(layerXML)
            print "OutGDB: "+gdb


            desc = arcpy.Describe(inFC)
            #Make sure feature is legite
            if desc.datasettype != "FeatureClass":
                print_message("Error! Expected a FeatureClass, got a " + desc.datasettype)
                sys.exit("")

            #If poly then Simplify poly
            if desc.ShapeType == "Polygon":
                try:
                    for key, value  in lyrInfo.iteritems():
                        arcpy.env.referenceScale = key
                        print key, value
                        outFC = inFC + "_" + key
                        printMessage(outFC)
                        if value:
                            outLyr = outFC+"_lyr"
                            DM.MakeFeatureLayer(inFC, outLyr,str(value))
                            print outLyr
                            try:
                                print "Working on level: "+ value +" with tolerance "+ str(getTolerance(key))
                                CA.SimplifyPolygon(outLyr,outFC,"POINT_REMOVE",getTolerance(key))


                            except:
                                printMessage("Failed at "+ key + " scale level")

                        else:
                            try:
                                print "Working on level: "+ value +" with tolerance "+ str(getTolerance(key))
                                CA.SimplifyPolygon(inFC,outFC,"POINT_REMOVE",getTolerance(key),"","NO_CHECK","NO_KEEP")
                            except:
                                printMessage("Failed at "+ key + " scale level")
                except:
                     for key, value  in enumerate(lyrInfo):
                        arcpy.env.referenceScale = value
                        print key, value
                        outFC = inFC + "_" + value
                        printMessage(outFC)
                        if value:
                            try:
                                print "Working on level: "+value +" with tolerance "+ str(getTolerance(value))
                                CA.SimplifyPolygon(inFC,outFC,"POINT_REMOVE",getTolerance(value),"","NO_CHECK","NO_KEEP")


                            except:
                                printMessage("Failed at "+ value + " scale level")

            # if line them simplify line
            if desc.ShapeType == "Polyline":
                   try:
                    for key, value  in lyrInfo.iteritems():
                        arcpy.env.referenceScale = key
                        print key, value
                        outFC = inFC + "_" + key
                        outFCSmooth = outFC + "_smoothed"
                        printMessage(outFC)
                        if value:
                            outLyr = outFC+"_lyr"
                            DM.MakeFeatureLayer(inFC, outLyr,str(value))
                            print outLyr
                            try:
                                print "Working on level: "+ str(getTolerance(key))
                                CA.SimplifyLine(outLyr,outFC,"POINT_REMOVE",getTolerance(key),"","NO_CHECK","NO_KEEP")


                            except:
                                printMessage("Failed at "+ key + " scale level")

                        else:
                            try:
                                print "Working on level: "+ str(getTolerance(key))
                                CA.SimplifyLine(inFC,outFC,"POINT_REMOVE",getTolerance(key),"","NO_CHECK","NO_KEEP")

                            except:
                                printMessage("Failed at "+ key + " scale level")
                   except:
                     for key, value  in enumerate(lyrInfo):
                        arcpy.env.referenceScale = value
                        print key, value
                        outFC = inFC + "_" + value
                        printMessage(outFC)
                        if value:
                            try:
                                print "Working on level: "+value +" with tolerance "+ str(getTolerance(value))
                                CA.SimplifyPolygon(inFC,outFC,"POINT_REMOVE",getTolerance(value),"","NO_CHECK","NO_KEEP")


                            except:
                                printMessage("Failed at "+ value + " scale level")





#input xml for vector layers
layerXML = arcpy.GetParameterAsText(0)
#myXML = (r"D:\Users\jemoore\workspace\PythonScripts\vector_pyramid_definitions.xml")
layerXML = minidom.parse(myXML)
# Fire the main function
startSimplify()





