#!/usr/bin/python
from pycaption import CaptionConverter
from pycaption import detect_format
from pycaption import SCCReader
from pycaption import DFXPWriter
from pycaption import SRTWriter
from bottle import route, run 

scc_caps = SCCReader().read("/Users/mathiesj/Desktop/Crop_detect/videos/test/HDXSP190A_1.scc", "r").read()
utf8Caps = unicode(scc_caps, "utf-8")
print SRTWriter().write(caps)
#print TranscriptWriter().write(caps)
#dfxp_caps = DFXPWriter().write(caps)
srt_caps = SRTWriter().write(utf8Caps)






#@route('/caption')
#def caption():
	#return dfxp_caps




#run(host='localhost', port=8080, debug=True)



#contents = SCCReader().read(input.decode('utf-8'))
#contents.get_captions('en-US') 