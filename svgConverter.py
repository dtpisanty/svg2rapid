import svgpathtools
import numpy as np

SVG_FILE="" # FILE'S ABSOLUTE PATH
RESOLUTION= 3 #pixels/mm
UNITS="mm" 
OUT_FILE=SVG_FILE.split('/')[-1].replace("svg","mod")
MODULE_NAME=OUT_FILE.split(".")[0]
TRAVEL_HEIGHT=5
DRAW_HEIGHT=0
WOBJ=""
TOOL=""
V_TRAVEL="v500"
V_DRAW="v50"
BEZIER_RESOLUTION=15
STATIC_ORIENT="[0,1,0,0]"
ROBOT_CONFIG="[0,0,0,0]"

EXTERNAL="[9E9,9E9,9E9,9E9,9E9,9E9]"
INDENT="  "

startPos=(0,0,TRAVEL_HEIGHT)
currentPos=[startPos[0],startPos[1],startPos[2]]

def vectAngles(vectA,vectB):
	return (vectA[0]/abs(vectA[0]))*np.arccos(np.dot(vectA,vectB)/(np.linalg.norm(vectA)*np.linalg.norm(vectB)))

def header():
	return """MODULE {modName}
{indent}VAR robtarget pos:=[[{sx:.2f},{sy:.2f},{sz:.2f}],{orient},{config},{external}];
{indent}VAR robtarget midpoint:=[[{sx:.2f},{sy:.2f},{sz:.2f}],{orient},{config},{external}];
{indent}CONST num zPos:=81;
{indent}PROC main()
""".format(modName=MODULE_NAME,sx=startPos[0],sy=startPos[1],sz=startPos[2],orient=STATIC_ORIENT,config=ROBOT_CONFIG,external=EXTERNAL,indent=INDENT)

def distance(target):
	# TODO
	global currentPos
	if (type(target)!=tuple and type(target)!=list) or len(target)!=3 :
		print("ERROR: Expected (x,y,z) tuple or list")
		return
	return np.sqrt()
def isCollinear(vect1,vect2):
	return not bool(np.cross(vect1,vect2))

def penUp():
	global currentPos
	currentPos[2]=TRAVEL_HEIGHT
	upPos=2*INDENT+"pos:=[[{x:.2f},{y:.2f},{z:.2f}],{orient},{config},{external}];\n".format(x=currentPos[0],y=currentPos[1],z=currentPos[2],orient=STATIC_ORIENT,config=ROBOT_CONFIG,external=EXTERNAL)
	return upPos+2*INDENT+"MoveL pos,{},fine,{} \\WObj:={};\n".format(V_TRAVEL,TOOL,WOBJ)

def penDown():
	global currentPos
	currentPos[2]=DRAW_HEIGHT
	downPos=2*INDENT+"pos:=[[{x:.2f},{y:.2f},{z:.2f}],{orient},{config},{external}];\n".format(x=currentPos[0],y=currentPos[1],z=currentPos[2],orient=STATIC_ORIENT,config=ROBOT_CONFIG,external=EXTERNAL)
	return downPos+2*INDENT+"MoveL pos,{},fine,{} \\WObj:={};\n".format(V_DRAW,TOOL,WOBJ)

def travelL(target):
	global currentPos
	if (type(target)!=tuple and type(target)!=list) or len(target)!=2 :
		print("ERROR: Expected (x,y) tuple or list")
		return
	currentPos=[-target[0]/RESOLUTION,target[1]/RESOLUTION,TRAVEL_HEIGHT]
	pos=2*INDENT+"pos:=[[{x:.2f},{y:.2f},{z:.2f}],{orient},{config},{external}];\n".format(x=currentPos[0],y=currentPos[1],z=currentPos[2],orient=STATIC_ORIENT,config=ROBOT_CONFIG,external=EXTERNAL)
	return penUp()+pos+2*INDENT+"MoveL pos,{},z5,{} \\WObj:={};\n".format(V_TRAVEL,TOOL,WOBJ)

def drawLine(target):
	global currentPos
	x=None
	y=None
	if (type(target)!=tuple and type(target)!=list and type(target)!=svgpathtools.path.Line):
		print("ERROR: Expected (x,y) tuple or list or svgpathtools.path.Line")
		return
	elif(len(target)!=2 ):
		print("ERROR: Expected x,y list/tuple of length 2")
		return
	if type(target)==svgpathtools.path.Line:
		x=-target.start.real
		y=target.start.imag
	else:
		x=-target[0]
		y=target[1]
	output=""
	currentPos=[x/RESOLUTION,y/RESOLUTION,DRAW_HEIGHT]
	output+=2*INDENT+"pos:=[[{x:.2f},{y:.2f},{z:.2f}],{orient},{config},{external}];\n".format(x=currentPos[0],y=currentPos[1],z=currentPos[2],orient=STATIC_ORIENT,config=ROBOT_CONFIG,external=EXTERNAL)
	output+=2*INDENT+"MoveL pos,{},z0,{} \\WObj:={};\n".format(V_DRAW,TOOL,WOBJ)
	return output

def drawArc(arcObject):
	global currentPos
	if type(arcObject)!=svgpathtools.path.Arc:
		"ERROR: Expected svgpathtools Arc object"
		return
	center=np.array([-arcObject.center.real,arcObject.center.imag])
	start=np.array([currentPos[0]-center[0],currentPos[1]-center[1]])
	end=np.array([-arcObject.end.real-center[0],arcObject.end.imag-center[1]])
	midAngle=vectAngles(start,end)/2
	print("#####")
	print(currentPos)
	print(arcObject.start.real,arcObject.start.imag)
	print(arcObject.end.real,arcObject.end.imag)
	print("c:{}, s:{}, e:{}, m:{}".format(center,start,end,midAngle))
	midPoint=np.array([(np.cos(midAngle)*arcObject.radius.real+center[0])/RESOLUTION,np.sin(midAngle)*arcObject.radius.imag+center[1]]/RESOLUTION)
	output=""
	currentPos=[-arcObject.end.real/RESOLUTION,arcObject.end.imag/RESOLUTION,DRAW_HEIGHT]
	output+=2*INDENT+"midpoint:=[[{x:.2f},{y.2f},{z:.2f}],{orient},{config},{external}];\n".format(x=midPoint[0],y=midPoint[1],z=currentPos[2],orient=STATIC_ORIENT,config=ROBOT_CONFIG,external=EXTERNAL)
	output+=2*INDENT+"pos:=[[{x:.2f},{y:.2f},{z:.2f}],{orient},{config},{external}];\n".format(x=currentPos[0],y=currentPos[1],z=currentPos[2],orient=STATIC_ORIENT,config=ROBOT_CONFIG,external=EXTERNAL)
	output+=2*INDENT+"MoveC midpoint,pos,{v},fine,{tool} \\WObj:={object};\n".format(v=V_DRAW,tool=TOOL,object=WOBJ)
	return output

def drawBezier(bezierObject):
	"""
	Aproximates bezier curve as a series of short, straight lines
	"""
	global currentPos
	output=""
	if type(bezierObject)!=svgpathtools.path.CubicBezier and type(bezierObject)!=svgpathtools.path.QuadraticBezier:
		print("ERROR: Expected svgpathtools Bezier object")
		return
	interpolations=np.array([t for t in range(1,BEZIER_RESOLUTION)])/BEZIER_RESOLUTION
	bzPoints=bezierObject.points(interpolations)
	# print("interpol",interpolations)
	for p in bzPoints:
		output+=drawLine((p.real,p.imag))	
	return output

# def drawQBezier():
# 	#TODO
# 	output=""
# 	output +=penDown
# 	return output

paths,attr,svg_attr=svgpathtools.svg2paths2(SVG_FILE)
paths.sort(key=lambda x: (x.bbox()[0]+x.bbox()[2])/2+(x.bbox()[1]+x.bbox()[3])/2)
rapid=header()
for p in paths:
	rapid+=travelL((p.start.real,p.start.imag))
	rapid+=penDown()
	for q in p:
		if type(q)==svgpathtools.path.Path:
			for r in q:
				if type(r)==svgpathtools.path.Arc:
					rapid+=drawArc(q)
				elif type(r)==svgpathtools.path.CubicBezier or type(q)==svgpathtools.path.QuadraticBezier:
					rapid+=drawBezier(r)
				else:
					rapid+=drawLine((q.end.real,q.end.imag))
		elif type(q)==svgpathtools.path.Arc:
			rapid+=drawArc(q)
		elif type(q)==svgpathtools.path.CubicBezier or type(q)==svgpathtools.path.QuadraticBezier:
			print(q)
			rapid+=drawBezier(q)
		else:
			rapid+=drawLine((q.end.real,q.end.imag))
	rapid+=penUp()
rapid+="\n"+INDENT+"ENDPROC"
rapid+="\nENDMODULE"
# print(rapid)
with open(OUT_FILE,'w') as f:
	f.write(rapid)
# p=paths[-2]