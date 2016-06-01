#!/usr/bin/python
from pycaption import CaptionConverter
from pycaption import detect_format
from pycaption import SCCReader
from pycaption import DFXPWriter
from pycaption import SRTWriter
from bottle import route, run 


scc_caps = open("/Users/mathiesj/Desktop/Crop_detect/videos/test/HDXSP190A_1.scc", "r").read()
print "SCC file loadout: %s" % scc_caps

caps = SCCReader().read(scc_caps.decode('utf-8'), offset=3600)
print DFXPWriter().write(caps).encode('utf-8')
print SRTWriter().write(caps).encode('utf-8')
srt_caps = SRTWriter().write(caps).encode('utf-8')
global dfxp_caps
dfxp_caps = DFXPWriter().write(caps).encode('utf-8')
with open("/Users/mathiesj/Desktop/Scripts/caption_samples/test_v1_offset.dfxp.xml", 'a') as dfxp_file:
	dfxp_file.write(dfxp_caps)

with open("/Users/mathiesj/Desktop/Crop_detect/videos/test/HDXSP190A_1.srt", 'a') as srt_file:
	srt_file.write(srt_caps)





#@route('/caption')
#def CaptionDFXPXML():
	#response.headers['Content-Type'] = 'xml/application'
	#return srt_caps




#run(host='localhost', port=8080, debug=True)


