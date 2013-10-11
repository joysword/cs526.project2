import omegaToolkit
import euclid
import math
from caveutil import *
from csv import reader


##############################################################################################################
# GLOBAL VARIABLES
def enum(**enums):
	return type('Enum', (), enums)

starTy = enum()
planetTy = enum()

## constants
c_scaleWall_size = 0.01
c_scaleWall_dist = 0.2

c_scaleCenter_size = 0.01
c_scaleCenter_dist = 0.2
c_scaleCenter_overall = 0.001

## global scale factors
g_scale_size = 1
g_scale_dist = 1
g_scale_time = 1

## unit conversion functions
def M_from_AU(n): # exact
	return n * 149597870700.0
def AU_from_M(n): # exact
	return n / 149597870700.0

def M_from_LY(n): # exact
	return n * 9460730472580800.0
def LY_from_M(n): # exact
	return n / 9460730472580800.0

def AU_from_PC(n): # exact
	return n * 648000.0 / math.pi * n
def PC_from_AU(n): # exact
	return n * math.pi / 648000.0

def M_from_PC(n):
	return M_from_AU(AU_from_PC(n))
def PC_from_M(n):
	return PC_from_AU(AU_from_M(n))

def AU_from_LY(n):
	return AU_from_M(M_from_LY(n))
def LY_from_AU(n):
	return LY_from_M(M_from_AU(n))

def LY_from_PC(n):
	return LY_from_M(M_from_PC(n))
def PC_from_LY(n):
	return PC_from_M(M_from_LY(n))

## column names in data file
g_c = {'name':0, 'star':1, 'size':2, 'distance':3, 'orbit':3, 'texture':4, 'rs':5, 'dec':6, 'app_mag':7, 'class':8, 'type':9, 'num':10, 'day':11, 'year':12, 'inc':13, 'detection':14}

## bolometric correction constant for calculating habitable zone
g_BC = {'B':-2.0,'A':-0.3,'F':-0.15,'G':-0.4,'K':-0.8,'M':-2.0}

##############################################################################################################
# CLASSES
class planet:
	def __init__(self,size,texture,orbit,name,day,year,inc,detection):
		self._size = float(size)
		self._texture = texture
		self._orbit = float(orbit)
		self._name = name
		self._day = float(day)
		self._year = float(year)
		self._inc = inc # TO DO
		self._detection = detection

class star:
	# _texture = ''
	# _mv = 0 # apparent magnitude
	# _radius = 0
	# _name = 'star'
	# _dis = 0 # distance to us in ly
	# _type = None # TO DO: starTy.xx
	# _class = 'Q' # class is the first letter of _type
	# _numChildren = 0
	# _children = []
	# _habNear = 0
	# _habFar = 0

	def __init__(self,t,mv,r,n,dis,c,ty,num):
		self._texture = t
		self._mv = float(mv)
		self._radius = float(r)
		self._name = n
		self._dis = float(dis) # TO DO: int?
		self._class = c
		self._type = ty
		self._numChildren = int(num)
		self._habNear, _habFar = self.getHabZone(self._mv, self._dis, self._class)
		self._children = []

	def addPlanet(self,pla):
		self._children.append(pla)

	def getHabZone(mv, dis, classs): # apparent magnitude, distance to us in ly, spectral class
		d = dis / 3.26156 # ly to parsec
		Mv = mv – 5*math.log10(d/10.0)
		Mbol = Mv + g_BC[classs]
		Lstar = math.pow(10, ((Mbol - 4.72)/-2.5))
		ri = math.sqrt(Lstar/1.1)
		ro = math.sqrt(Lstar/0.53)
		return ri,ro

class plaSys:
	def __init__(self,star,dis,name):
		self._star = star
		self._dis = dis
		self._name = name

##############################################################################################################
# PLAY SOUND
sdEnv = getSoundEnvironment()
sdEnv.setAssetDirectory('syin_p2')

sd_warn = SoundInstance(sdEnv.loadSoundFromFile('warn',"sound/warn.wav"))
sd_bgm = SoundInstance(sdEnv.loadSoundFromFile('backgroundmusic',"sound/bgm.wav"))
sd_load = SoundInstance(sdEnv.loadSoundFromFile('load',"sound/load.wav"))

def playSound(sd, pos, vol):
	sd.setPosition(pos)
	sd.setVolume(vol)
	sd.setWidth(20)
	sd.play()

##############################################################################################################
# CREATE MENUS

mm = MenuManager.createAndInitialize()

## menu to change scale factor
menu_scale = mm.getMainMenu().addSubMenu('change scale factor')
scaleWidget = menu_scale.addContainer()
scaleContainer = scaleWidget.getContainer()
scaleContainer.setLayout(ContainerLayout.LayoutHorizontal)
scaleContainer.setMargin(0)

scaleSizeLabel = Label.create(scaleContainer)
scaleSizeLabel.setText('size: ')

scaleSizeBtnContainer = Container.create(ContainerLayout.LayoutVertical, scaleContainer)
scaleSizeBtnContainer.setPadding(-4)

scaleSizeUpBtn = Button.create(scaleSizeBtnContainer)
scaleSizeUpBtn.setText("+")
scaleSizeUpBtn.setUIEventCommand('changeScale("size", True)')

scaleSizeDownBtn = Button.create(scaleSizeBtnContainer)
scaleSizeDownBtn.setText("-")
scaleSizeDownBtn.setUIEventCommand('changeScale("size", False)')

scaleDistLabel = Label.create(scaleContainer)
scaleDistLabel.setText('distance: ')

scaleDistBtnContainer = Container.create(ContainerLayout.LayoutVertical, scaleContainer)
scaleDistBtnContainer.setPadding(-4)

scaleDistUpBtn = Button.create(scaleDistBtnContainer)
scaleDistUpBtn.setText('+')
scaleDistUpBtn.setUIEventCommand('changeScale("dist", True)')

scaleDistDownBtn = Button.create(scaleDistBtnContainer)
scaleDistDownBtn.setText('-')
scaleDistDownBtn.setUIEventCommand('changeScale("dist", False)')

scaleSizeUpBtn.setHorizontalNextWidget(scaleDistUpBtn)
scaleDistUpBtn.setHorizontalPrevWidget(scaleSizeUpBtn)
scaleSizeDownBtn.setHorizontalNextWidget(scaleDistDownBtn)
scaleDistDownBtn.setHorizontalPrevWidget(scaleSizeDownBtn)

# TO DO: ADD value

## menu to change time speed
menu_speed = mm.getMainMenu().addSubMenu('change time speed')
speedWidget = menu_speed.addContainer()
speedContainer = speedWidget.getContainer()
speedContainer.setLayout(ContainerLayout.LayoutHorizontal)
speedContainer.setMargin(0)

speedLabel = Label.create(speedContainer)
speedLabel.setText('time speed: ')

speedBtnContainer = Container.create(ContainerLayout.LayoutVertical, speedContainer)
speedBtnContainer.setPadding(-4)

speedUpBtn = Button.create(speedBtnContainer)
speedUpBtn.setText('+')
speedUpBtn.setUIEventCommand('changeScale("time", True)')

speedDownBtn = Button.create(speedBtnContainer)
speedDownBtn.setText('-')
speedDownBtn.setUIEventCommand('changeScale("time", False)')

# TO DO: ADD value

## menu to change other things
#
#

## update the scale factor to all the visualizations
def updateScale(name, add):
	if cmp(name, 'dist')==0: # dist
		# TO DO: update all small multiples
		# TO DO: update 3D in center
		todo = 0

	elif cmp(name, 'size')==0:
		# TO DO: update all small multiples
		# TO DO: update 3D in center
		todo = 0

	elif cmp(name, 'time')==0:
		# TO DO: update 3D in center
		todo = 0

## change the scale factor, if failed return False
def changeScale(name, add):
	global g_scale_size
	global g_scale_dist

	if cmp(name,'dist')==0: # dist
		if add: # +
			g_scale_dist=g_scale_dist+0.25
			if g_scale_dist>5:
				g_scale_dist=5
				return False
			else: # update the scene
				foreach
		else: # -
			g_scale_dist=g_scale_dist-0.25
			if g_scale_dist<0.25:
				g_scale_dist=0.25
				return False
	elif cmp(name,'size')==0:
		if add: # +
			g_scale_size=g_scale_size+0.25
			if g_scale_size>5:
				g_scale_size=5
				return False
		else: # -
			g_scale_size=g_scale_size-0.25
			if g_scale_size<0.25:
				g_scale_size=0.25
				return False
	elif cmp(name,'time')==0:
		if add: # +
			g_scale_time=g_scale_time*2
			if g_scale_time>16:
				g_scale_time=16
				return False
		else: # -
			g_scale_time=g_scale_time/2.0
			if g_scale_time<0.25:
				g_scale_time=0.25
				return False
	updateScale(name, add)
	return True

##############################################################################################################
# INITIALIZE THE SCENE
scene = getSceneManager()
cam = getDefaultCamera()

#set the background to black - kinda spacy
scene.setBackgroundColor(Color(0, 0, 0, 1))

#set the far clipping plane back a bit
setNearFarZ(0.1, 1000000)

sn_root = SceneNode.create('root')
sn_centerSys = SceneNode.create('centerSystem')
sn_smallMulti = SceneNode.create('smallMulti')
#sn_allSystems = SceneNode.create('allSystems')

sn_root.addChild(sn_centerSys)
sn_root.addChild(sn_smallMulti)
#sn_smallMulti.addChild(sn_allSystems)

## Create a directional light
light1 = Light.create()
light1.setLightType(LightType.Point)
light1.setColor(Color(1.0, 1.0, 1.0, 1.0))
#light1.setPosition(Vector3(0.0, 1.5, 1.0))
light1.setPosition(Vector3(0.0, 0.0, 0.0))
light1.setEnabled(True)

## Load default sphere model
mi = ModelInfo()
mi.name = "defaultSphere"
mi.path = "sphere.obj"
scene.loadModel(mi)

##############################################################################################################
# LOAD DATA FROM FILE

curStar = None
li_allSys = [];

f = open('data.csv','rb')
lines = reader(f)
for p in lines:
	if p[g_c['star']]==1: # star
		# def __init__(self,t,mv,r,n,dis,c,ty,num):
		curStar = star(p[g_c['texture']], p[g_c['app_mag']], p[g_c['size']], p[g_c['name']], p[g_c['distance']], p[g_c['class']], p[g_c['type']], p[g_c['num']])
		curSys = plaSys(curStar,curStar._dis,curStar._name)
		li_allSys.append(curSys)

	else: # planet
		# def __init__(self,size,texture,orbit,name,day,year,inc,detection):
		curPla = planet(p[g_c['size']], p[g_c['texture']], p[g_c['size']], p[g_c['orbit']], p[g_c['name']], p[g_c['day']], p[g_c['year']], p[g_c['inc']], p[g_c['detection']])
		curStar.addPlanet(curPla)
print 'number of systems generated:', len(li_allSys)

##############################################################################################################
# INITIALIZE SMALL MULTIPLES

def initSmallMulti():
	global li_allSys

	smallCount = 0

	for col in xrange(0, 18):

		# leave a 'hole' in the center of the cave to see the far planets through
		if col>=6 and col<=11:
			continue

		for row in xrange(0, 8):

			curSys = li_allSys[smallCount]

			bs_outlineBox = BoxShape.create(2.0, 0.25, 0.001)
			bs_outlineBox.setPosition(Vector3(-0.5, 0, 0.01))
			bs_outlineBox.setEffect('colored -e #111111')

			sn_smallTrans = SceneNode.create("smallTrans"+str(smallCount))
			sn_smallSys = SceneNode.create("smallSys"+str(smallCount))

			## get star
			habOuter = curSys._star._habFar
			habInner = curSys._star._habNear

			if caveutil.isCAVE():
				t = Text3D.create('fonts/arial.ttf', 120, name + " - " + curSys._star._type) # type
			else:
				t = Text3D.create('fonts/arial.ttf', 10, name + " - " + curSys._star._type) # type
			#t.setPosition(Vector3(-0.2, 0.05, -0.5))
			t.setPosition(Vector3(-0.2, 0.05, -0.05))
			t.yaw(3.14159)
			#t.setFontResolution(120)
			#t.getMaterial().setDoubleFace(1)
			t.getMaterial().setTransparent(False)
			t.getMaterial().setDepthTestEnabled(False)
			#t.setFixedSize(True)
			t.setColor(Color('white'))
			sn_smallTrans.addChild(t)

			model = BoxShape.create(100, 25000, 2000)
			model.setPosition(Vector3(0.0, 0.0, 48000)# - thisSystem[name][1] * XorbitScaleFactor * user2ScaleFactor))
			sn_smallSys.addChild(model)
			model.setEffect("textured -v emissive -d "+curSys._star._texture)

			### get habitable zone if it is in the range
			if habInner < wallLimit:
				if habOuter > wallLimit:
					habOuter = wallLimit
				habCenter = (habOuter+habInner)/2.0
				bs_goldi = BoxShape.create(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
				bs_goldi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
				sn_smallSys.addChild(bs_goldi)
				bs_goldi.setEffect('colored -e #006110')
				#bs_goldi.getMaterial().setTransparent(True)

			## get planets
			outCounter = 0
			for p in curSys._star._children:
				model = StaticObject.create("defaultSphere")
				model.setScale(Vector3(p._size * c_scaleWall_size * g_scale_size, p._size * c_scaleWall_size * g_scale_size, p._size * c_scaleWall_size * g_scale_size))
				model.setPosition(Vector3(0.0,0.0,48000 - p._orbit * c_scaleWall_dist * g_scale_dist))
				model.setEffect('textured -v emissive -d '+p._texture)
				sn_smallSys.addChild(model)
				if p._orbit > wallLimit:
					outCounter+=1
					model.setVisible(False)


			sn_smallSys.yaw(pi/2.0)
			sn_smallSys.setScale(0.0000001, 0.00001, 0.00001) #scale for panels - flat to screen

			hLoc = h + 0.5
			degreeConvert = 36.0/360.0*2*pi #18 degrees per panel times 2 panels per viz = 36
			caveRadius = 3.25
			sn_smallTrans.setPosition(Vector3(sin(hLoc*degreeConvert)*caveRadius, row * 0.29 + 0.41, cos(hLoc*degreeConvert)*caveRadius))
			sn_smallTrans.yaw(hLoc*degreeConvert)

			sn_smallTrans.addChild(sn_smallSys)
			sn_smallTrans.addChild(bs_outlineBox)

			sn_smallMulti.addChild(sn_smallTrans)

			smallCount += 1

initSmallMulti()

##############################################################################################################
# INIT 3D SOLAR SYSTEM

def addOrbit(orbit, thick):
	circle = LineSet.create()

	segments = 128
	radius = 1
	thickness = thick   #0.01 for orbit

	a = 0.0
	while a <= 360:
		x = cos(radians(a)) * radius
		y = sin(radians(a)) * radius
		a += 360.0 / segments
		nx = cos(radians(a)) * radius
		ny = sin(radians(a)) * radius

		l = circle.addLine()
		l.setStart(Vector3(x, 0, y))
		l.setEnd(Vector3(nx, 0, ny))
		l.setThickness(thickness)

		circle.setPosition(Vector3(0, 2, -4))

		circle.setEffect('colored -e white')

		# Squish z to turn the torus into a disc-like shape.

		circle.setScale(Vector3(orbit, 1000.0, orbit))

		sn_centerTrans.addChild(circle)

def initCenter(verticalHeight, theSys):
	#global sn_centerSys

	sn_centerTrans = SceneNode.create('centerTrans'+theSys._name)
	sn_centerSys.addChild(sn_centerTrans)

	## the star
	model = StaticObject.create('defaultSphere')
	model.setScale(Vector3(theSys._star._size*c_scaleCenter_size*g_scale_size, theSys._star._size*c_scaleCenter_size*g_scale_size, theSys._star._size*c_scaleCenter_size*g_scale_size))
	model.getMaterial().setProgram('textured')
	model.setEffect("textured -v emissive -d "+theSys._star._texture)

	# activePlanets[name] = model

	sunDot = StaticObject.create("defaultSphere")
	#sunDot.setPosition(Vector3(0.0, 0.0, 0.0))
	sunDot.setScale(Vector3(10, 10, 10))
	sn_centerTrans.addChild(sunDot)

	sunLine = LineSet.create()

	l = sunLine.addLine()
	l.setStart(Vector3(0, 0, 0))
	l.setEnd(Vector3(0, 1000, 0))
	l.setThickness(1)
	sunLine.setEffect('colored -e white')
	sn_centerTrans.addChild(sunLine)

	sn_planetCenter = SceneNode.create('planetCenter'+theSys._star._name)

	## tilt
	sn_tiltCenter = SceneNode.create('tiltCenter'+theSys._star._name)
	sn_planetCenter.addChild(sn_tiltCenter)
	sn_tiltCenter.addChild(model)
	#sn_tiltCenter.roll(theSystem[name][6]/180.0*math.pi)

	## rotation
	sn_rotCenter = SceneNode.create('rotCenter'+theSys._star._name)
	sn_rotCenter.setPosition(Vector3(0,0,0))
	sn_rotCenter.addChild(sn_planetCenter)

	#activeRotCenters[name] = rotCenter
	sn_centerTrans.addChild(sn_rotCenter)

	# addOrbit(theSystem[name][1]*orbitScaleFactor*userScaleFactor, 0, 0.01)

	# deal with labelling everything
	v = Text3D.create('fonts/arial.ttf', 120, theSys._star._name)
	v.setPosition(Vector3(0, 500, 0))
	#v.setFontResolution(120)

	#v.setFontSize(160)
	v.getMaterial().setDoubleFace(1)
	v.setFixedSize(True)
	v.setColor(Color('white'))
	sn_planetCenter.addChild(v)

	## the planets
	for p in theSys._star._children:
		model.setPosition(Vector3(0.0, 0.0, -p._orbit*g_scale_dist*c_scaleCanter_dist))
		model.setScale(Vector3(p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size))
		model.getMaterial().setProgram('textured')
		model.setEffect('textured -d '+p._texture)

		#activePlanets[name] = model

		#set up for planet name on top of planet
		sn_planetCenter = SceneNode.create('planetCenter'+theSys._name+p._name)

		# deal with the axial tilt of the sun & planets
		sn_tiltCenter = SceneNode.create('tiltCenter'+theSys._name+p._name)
		sn_planetCenter.addChild(sn_tiltCenter)
		sn_tiltCenter.addChild(model)
		#sn_tiltCenter.roll(theSystem[name][6]/180.0*math.pi)

		# deal with rotating the planets around the sun
		sn_rotCenter = SceneNode.create('rotCenter'+theSys._name+p._name)
		sn_rotCenter.setPosition(Vector3(0,0,0))
		sn_rotCenter.addChild(sn_planetCenter)

		#activeRotCenters[name] = rotCenter
		sn_centerTrans.addChild(sn_rotCenter)

		addOrbit(p._orbit*g_scale_dist*c_scaleCanter_dist, 0.01)

		# deal with labelling everything
		v = Text3D.create('fonts/arial.ttf', 120, p._name)
		v.setPosition(Vector3(0, p._orbit*c_scaleCenter_dist*g_scale_dist, - p._orbit*c_scaleCenter_dist*g_scale_dist))
		#v.setFontResolution(120)

		#v.setFontSize(160)
		v.getMaterial().setDoubleFace(1)
		v.setFixedSize(True)
		v.setColor(Color('white'))
		sn_planetCenter.addChild(v)

	## deal with the habitable zone

	cs_inner = CylinderShape.create(1, theSys._star._habNear*c_scaleCanter_dist*g_scale_dist, theSys._star._habNear*c_scaleCanter_dist*g_scale_dist, 8, 128)
	cs_inner.setEffect('colored -e #ff000055')
	cs_inner.getMaterial().setTransparent(True)
	cs_inner.pitch(-3.14159*0.5)
	cs_inner.setScale(Vector3(1, 1, 1.0))

	cs_outer = CylinderShape.create(1, theSys._star._habFar*c_scaleCanter_dist*g_scale_dist, theSys._star._habFar*c_scaleCanter_dist*g_scale_dist, 8, 128)
	cs_outer.setEffect('colored -e #00FF0055')
	cs_outer.getMaterial().setTransparent(True)
	cs_outer.pitch(-3.14159*0.5)
	cs_outer.setScale(Vector3(1, 1, 0.1))

	sn_habZone = SceneNode.create("habZone")
	sn_habZone.addChild(cs_outer)
	sn_habZone.addChild(cs_inner)

	sn_centerTrans.addChild(sn_habZone)
	sn_centerTrans.addChild(light1)

	## add everything to the sn_centerTrans node for scaling and default positioning
	sn_centerTrans.setScale(Vector3(c_scaleCenter_overall, c_scaleCenter_overall, c_scaleCenter_overall))
	sn_centerTrans.setPosition(Vector3(0, verticalHeight, 1))

	## end here


##############################################################################################################
# EVENT FUNCTION

def onEvent():
	global g_scale_size
	global g_scale_dist

	e = getEvent()

	if e.isButtonDown(EventFlags.ButtonLeft):
		if not changeScale('dist',False):
			playSound(sd_warn, e.getPosition(), 1.0)
	elif e.isButtonDown(EventFlags.ButtonRight):
		if not changeScale('dist',True):
			playSound(sd_warn, e.getPosition(), 1.0)
	elif e.isButtonDown(EventFlags.ButtonUp):
		if not changeScale('size',True):
			playSound(sd_warn, e.getPosition(), 1.0)
	elif e.isButtonDown(EventFlags.ButtonDown):
		if not changeScale('size',False):
			playSound(sd_warn, e.getPosition(), 1.0)

	## reset the scene
	elif e.isButtonDown(EventFlags.Button5):
		g_scale_size = 1
		g_scale_dist = 1
		reset3D() # TO DO: put solar system on center
		resetWall() # TO DO: put default small multiples on the wall

	elif e. isButtonDown(EventFlags.Button5):
		if not changeScale('time',False):
			playSound(sd_warn, e.getPosition(), 1.0)

setEventFunction(onEvent)

##############################################################################################################
# UPDATE FUNCTION

def onUpdate(frame, t, dt):

	# ALL THINGS IN 3D ROTATE AS TIME PASSES BY
	for i in xrange(sn_centerSys.numChild()):
		sn_centerSys.getChildByIndex(i)
		activeRotCenters[name].yaw(dt/40*(1.0 / currentSystem[name][3])) #revolution (year)
		activePlanets[name].yaw(dt/40*365*(1.0 / currentSystem[name][4])) #rotation (day)

setUpdateFunction(onUpdate)


#### THE END #################################################################################################
