import omegaToolkit
import euclid
import math
from caveutil import *
from csv import reader

##############################################################################################################
# GLOBAL VARIABLES
g_changeSizeWallText = []

g_changeSize = []
g_changeSizeCenterText = []

g_changeDistCircles = []
g_changeDistCenterPlanets = []
g_changeDistCenterHab = []

g_orbit = []
g_rot = []

g_cen_changeSize = []
g_cen_changeSizeCenterText = []
g_cen_changeDistCircles = []
g_cen_changeDistCenterPlanets = []
g_cen_changeDistCenterHab = []
g_cen_orbit = []
g_cen_rot = []

g_reorder = 0 # status of reorder 0: not; 1: select; 2: moving

g_moveToCenter = 0 # status of bring to center 0: not; 1: in

g_invisOnes = []

li_allSys = []; # classes, aaalllllll the systems
dic_allBox = {}; # dictionary of systems
li_boxOnWall = [] # scenenodes (outlineBox)

wallLimit = 247000000 # by default, everything closer than this numer can be shown

## constants
caveRadius = 3.25
c_col_on_wall = 6
c_row_on_wall = 8

WALLLIMIT = 247000000 # wallLimit will change, WALLLIMIT won't

c_scaleWall_size = 0.2
c_scaleWall_dist = 0.0008

c_scaleCenter_size = 0.01
c_scaleCenter_dist = 0.000005
c_scaleCenter_overall = 0.00025

c_smallLabel_y_cave = 0.08

R_jupiter = 69911 # in KM
R_sun = 695500 # in KM
M_earth = 5.97219e24 # in KG

## global scale factors
g_scale_size = 1.0
g_scale_dist = 1.0
g_scale_time = 1.0

## font size
g_ftszdesk = 0.03
g_ftszcave = 0.03
g_ftszcave_center = 120

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

def KM_from_AU(n): # exact
	return n * 149597870.7

## column names in data file
g_c = {'name':0, 'star':1, 'size':2, 'distance':3, 'orbit':3, 'texture':4, 'rs':5, 'dec':6, 'app_mag':7, 'class':8, 'type':9, 'num':10, 'day':11, 'year':12, 'inc':13, 'detection':14, 'mass':15}

## bolometric correction constant for calculating habitable zone
g_BC = {'B':-2.0,'A':-0.3,'F':-0.15,'G':-0.4,'K':-0.8,'M':-2.0}

def CAVE():
	return caveutil.isCAVE();

##############################################################################################################
# CLASSES
class planet:
	def __init__(self,size,texture,orbit,name,day,year,inc,detection,mass):
		if cmp(size,'')==0:
			if cmp(mass,'')==0:
				self._mass = 0
				self._size = 0
			else:
				self._mass = float(mass) * M_earth
				self._size = self.__getSizeFromMass(self._mass)
				print 'size:',self._size
		else:
			self._size = float(size) * R_jupiter # to KM
			self._mass = 0
		self._texture = texture
		if cmp(orbit,'')==0:
			self._orbit = 0
		else:
			self._orbit = KM_from_AU(float(orbit)) # to KM
		self._name = name
		if cmp(day,'')==0:
			self._day = 0
		else:
			self._day = float(day)
		if cmp(year,'')==0:
			self._year = 0
		else:
			self._year = float(year)
		if cmp(inc,'')==0:
			self._inc = 0
		else:
			self._inc = float(inc)
		if cmp(detection,'')==0:
			self._detection = 'unknown'
		else:
			self._detection = detection
		#self._model = None

		def __getSizeFromMass(mass):
			print 'mass:',mass
			if mass<5e25:
				return 0.5501*(mass**0.2858)*0.001 # to KM
			elif mass<1e27:
				return 7e-8*(mass**0.5609)*0.001 # to KM
			else:
				return 4e8*(mass**-0.0241)*0.001 # to KM

class star:
	def __init__(self,t,mv,size,n,dis,c,ty,num):
		self._texture = t
		if cmp(mv,'')==0:
			self._mv = 0
		else:
			self._mv = float(mv)
		#print 'mv:',mv
		#print 'slef._mv:',self._mv
		if cmp(size,'')==0:
			self._size = 0
		else:
			self._size = float(size) * R_sun
		self._name = n
		self._dis = int(dis)
		if cmp(c,'')==0:
			self._class = 'unknown'
		else:
			self._class = c
		if cmp(ty,'')==0:
			self._type = 'unknown'
		else:
			self._type = ty
		self._numChildren = int(num)
		if self._mv==0 or cmp(self._class,'unkown')==0:
			self._habNear = 0
			self._habFar = 0
		else:
			self._habNear, self._habFar = self.getHabZone(self._mv, self._dis, self._class) # in KM
		self._children = []

	def addPlanet(self,pla):
		self._children.append(pla)

	def getHabZone(self, mv, dis, classs): # apparent magnitude, distance to us in ly, spectral class
		if cmp(self._name,'Sun') == 0:
			ri = math.sqrt(1.0/1.1)
			ro = math.sqrt(1.0/0.53)
			return KM_from_AU(ri),KM_from_AU(ro)
		else:
			d = dis / 3.26156 # ly to parsec
			#print 'd:',d
			Mv = mv - 5 * math.log10( d/10.0 )
			if not classs in g_BC:
				return 0,0
			Mbol = Mv + g_BC[classs]
			Lstar = math.pow(10, ((Mbol - 4.72)/-2.5))
			ri = math.sqrt(Lstar/1.1)
			ro = math.sqrt(Lstar/0.53)
			return KM_from_AU(ri),KM_from_AU(ro)

class plaSys:
	def __init__(self,star,dis,name):
		self._star = star
		self._dis = dis
		self._name = name

##############################################################################################################
# PLAY SOUND
sdEnv = getSoundEnvironment()
sdEnv.setAssetDirectory('syin_p2')

sd_warn = SoundInstance(sdEnv.loadSoundFromFile('warn','sound/warn.wav'))
sd_bgm = SoundInstance(sdEnv.loadSoundFromFile('backgroundmusic','sound/bgm.wav'))
sd_load = SoundInstance(sdEnv.loadSoundFromFile('load','sound/load.wav'))

sd_reo_please = SoundInstance(sdEnv.loadSoundFromFile('reo_please','sound/reorder/please.wav'))
sd_reo_selected = SoundInstance(sdEnv.loadSoundFromFile('reo_selected','sound/reorder/selected.wav'))
sd_reo_done = SoundInstance(sdEnv.loadSoundFromFile('reo_done','sound/reorder/done.wav'))
sd_reo_quit = SoundInstance(sdEnv.loadSoundFromFile('reo_quit','sound/reorder/quit.wav'))

sd_mtc_please = SoundInstance(sdEnv.loadSoundFromFile('mtc_please','sound/movetocenter/please.wav'))
sd_mtc_moving = SoundInstance(sdEnv.loadSoundFromFile('mtc_moving','sound/movetocenter/moving.wav'))

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
scaleSizeUpBtn.setText('+')
scaleSizeUpBtn.setUIEventCommand('changeScale("size", True)')

scaleSizeDownBtn = Button.create(scaleSizeBtnContainer)
scaleSizeDownBtn.setText('-')
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

## button to hide/show small multiples
btn_hideWall = mm.getMainMenu().addButton('hide small multiples','toggleWallVisible()')

## button to move one of the small multiples to center
btn_moveToCenter = mm.getMainMenu().addButton('move to center','startMoveToCenter()')

## button to reorder the small multiples
btn_reorder = mm.getMainMenu().addButton('reorder small multiples','startReorder()')

## button to reset the scene
btn_reset = mm.getMainMenu().addButton('reset the scene','resetEverything()')

##############################################################################################################
# INITIALIZE THE SCENE
scene = getSceneManager()
cam = getDefaultCamera()

#set the background to black - kinda spacy
scene.setBackgroundColor(Color(0, 0, 0, 1))

#set the far clipping plane back a bit
setNearFarZ(0.1, 1000000)

sn_root = SceneNode.create('root')
sn_centerSys = SceneNode.create('centerSystems')
sn_cen_sys = SceneNode.create('cen_sys')# another system in center
sn_smallMulti = SceneNode.create('smallMulti')
#sn_allSystems = SceneNode.create('allSystems')

sn_root.addChild(sn_centerSys)
sn_root.addChild(sn_smallMulti)
#sn_smallMulti.addChild(sn_allSystems)
sn_centerSys.addChild(sn_cen_sys)

# fix small multiples, no move
if CAVE():
	cam.addChild(sn_smallMulti)

## Create a directional light
light1 = Light.create()
light1.setLightType(LightType.Point)
light1.setColor(Color(1.0, 1.0, 1.0, 1.0))
#light1.setPosition(Vector3(0.0, 1.5, 1.0))
light1.setPosition(Vector3(0.0, 0.0, 0.0))
light1.setEnabled(True)

## Load default sphere model
mi = ModelInfo()
mi.name = 'defaultSphere'
mi.path = 'sphere.obj'
scene.loadModel(mi)

## pointer for selecting
pointer = SphereShape.create(0.01,3)
pointer.setEffect('colored -e #ff6600')
pointer.setVisible(False)

##############################################################################################################
# LOAD DATA FROM FILE

atLine = 0
f = open('data1.csv','rU')
lines = reader(f)
for p in lines:
	atLine+=1
	if (atLine == 1):
		continue
	print 'line:',atLine
	#print p
	if int(p[g_c['star']])==1: # star
		# def __init__(self,t,mv,r,n,dis,c,ty,num):
		curStar = star(p[g_c['texture']], p[g_c['app_mag']], p[g_c['size']], p[g_c['name']], p[g_c['distance']], p[g_c['class']], p[g_c['type']], p[g_c['num']])
		curSys = plaSys(curStar,curStar._dis,curStar._name)
		li_allSys.append(curSys)
		#dic_allSys[curSys._name] = curSys

	else: # planet
		# def __init__(self,size,texture,orbit,name,day,year,inc,detection):
		curPla = planet(p[g_c['size']], p[g_c['texture']], p[g_c['orbit']], p[g_c['name']], p[g_c['day']], p[g_c['year']], p[g_c['inc']], p[g_c['detection']], p[g_c['mass']])
		#print 'mass:',curPla._mass
		#print 'size:',curPla._size
		curStar.addPlanet(curPla)

print 'number of systems generated:', len(li_allSys)


##############################################################################################################
# INITIALIZE SMALL MULTIPLES

def initSmallMulti():

	global li_boxOnWall

	smallCount = 0

	for col in xrange(0, 9):

		# leave a 'hole' in the center of the cave to see the far planets through
		if col>=3 and col<=5:
			continue

		for row in xrange(0, 8):

			#print 'smallCount:',smallCount
			curSys = li_allSys[smallCount]

			sn_smallTrans = SceneNode.create('smallTrans'+str(smallCount))

			bs_outlineBox = BoxShape.create(2.0, 0.25, 0.001)
			bs_outlineBox.setPosition(Vector3(-0.5, 0, 0.01))
			bs_outlineBox.setEffect('colored -e #01b2f144')
			bs_outlineBox.getMaterial().setTransparent(True)

			#sn_smallSys = SceneNode.create('smallSys'+str(smallCount))
			sn_smallSys = SceneNode.create('smallSys')

			#li_sysOnWall.append(sn_smallTrans)
			li_boxOnWall.append(bs_outlineBox)
			dic_allBox[bs_outlineBox] = curSys

			## get star
			bs_model = BoxShape.create(100, 25000, 2000)
			bs_model.setPosition(Vector3(0.0, 0.0, 48000))# - thisSystem[name][1] * XorbitScaleFactor * user2ScaleFactor))
			bs_model.setEffect('textured -v emissive -d '+curSys._star._texture)
			sn_smallSys.addChild(bs_model)

			## get habitable zone if it is in the range
			habOuter = curSys._star._habFar
			habInner = curSys._star._habNear

			sn_habiParent = SceneNode.create('habiParent'+str(smallCount))

			bs_habi = BoxShape.create(1, 1, 1)

			if habInner < wallLimit:
				if habOuter > wallLimit:
					habOuter = wallLimit
				habCenter = (habOuter+habInner)/2.0
			else:
				bs_habi.setVisible(False)

			bs_habi.setScale(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
			bs_habi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
			bs_habi.setEffect('colored -e #00611055')
			bs_habi.getMaterial().setTransparent(True)

			sn_smallSys.addChild(sn_habiParent)
			sn_habiParent.addChild(bs_habi)
				#sn_smallSys.addChild(bs_habi) # child 1

			sn_smallTrans.addChild(sn_smallSys)
			sn_smallTrans.addChild(bs_outlineBox)

			## get planets
			sn_planetParent = SceneNode.create('planetParent'+str(smallCount))

			outCounter = 0
			for p in curSys._star._children:
				#model = StaticObject.create('defaultSphere')
				model = SphereShape.create(p._size * c_scaleWall_size * g_scale_size, 4)
				#model.setScale(Vector3(p._size * c_scaleWall_size * g_scale_size, p._size * c_scaleWall_size * g_scale_size, p._size * c_scaleWall_size * g_scale_size))
				model.setPosition(Vector3(0.0,0.0,48000 - p._orbit * c_scaleWall_dist * g_scale_dist))
				g_changeSize.append(model)
				model.setEffect('textured -v emissive -d '+p._texture)
					#sn_smallSys.addChild(model)
				sn_planetParent.addChild(model)
				t = Text3D.create('fonts/helvetica.ttf', 1, p._name)
				#print '!!name:',p._name
				if CAVE():
					#t.setFontResolution(120)
					#t.setFontSize(120)
					t.setFontSize(64)
				else:
					t.setFontSize(g_ftszdesk)
				t.setPosition(Vector3(0.0, p._size * c_scaleWall_size * g_scale_size, 48000 - p._orbit * c_scaleWall_dist * g_scale_dist))
				g_changeSizeWallText.append(t)
				t.yaw(0.5*math.pi) # back to face, face to back
				#t.setFontResolution(120)
				#t.getMaterial().setDoubleFace(1)
				t.getMaterial().setTransparent(False)
				t.getMaterial().setDepthTestEnabled(False)
				t.setFixedSize(True)
				t.setColor(Color('white'))
				sn_planetParent.addChild(t)
				if p._orbit > wallLimit:
					outCounter+=1
					model.setVisible(False)
					t.setVisible(False)

			sn_smallSys.addChild(sn_planetParent)

			## get text
			t = Text3D.create('fonts/helvetica.ttf', 1, curSys._name+' | type: '+curSys._star._type+' | distance: '+str(curSys._star._dis)+' ly | planets discovered by: '+curSys._star._children[0]._detection)
			if CAVE():
				#t.setFontResolution(120)
				#t.setFontSize(120)
				t.setFontSize(g_ftszcave)
			else:
				#t.setFontResolution(10)
				t.setFontSize(g_ftszdesk)
			if CAVE():
				t.setPosition(Vector3(0.3, c_smallLabel_y_cave, -0.01))
			else:
				t.setPosition(Vector3(0.3, 0.08, -0.01))
			t.yaw(math.pi) # back to face, face to back
			#t.setFontResolution(120)
			#t.getMaterial().setDoubleFace(1)
			t.getMaterial().setTransparent(False)
			t.getMaterial().setDepthTestEnabled(False)
			#t.setFixedSize(True)
			t.setColor(Color('white'))
			sn_smallTrans.addChild(t)

			## get indicator if some planets are outside
			sn_indicatorParent = SceneNode.create('indicatorParent'+str(smallCount))

			t = Text3D.create('fonts/helvetica.ttf', 1, str(outCounter)+' more planet(s) -->>')
			if CAVE():
				#t.setFontResolution(120)
				#t.setFontSize(120)
				t.setFontSize(g_ftszcave)
			else:
				#t.setFontResolution(10)
				t.setFontSize(g_ftszdesk)
			if CAVE():
				t.setPosition(Vector3(-1.15, c_smallLabel_y_cave, -0.01))
			else:
				t.setPosition(Vector3(-0.9, 0.08, -0.01))
			t.yaw(math.pi) # back to face, face to back
			#t.setFontResolution(120)
			#t.getMaterial().setDoubleFace(1)
			t.getMaterial().setTransparent(False)
			t.getMaterial().setDepthTestEnabled(False)
			#t.setFixedSize(True)
			t.setColor(Color('white'))
			sn_smallTrans.addChild(sn_indicatorParent)
			sn_indicatorParent.addChild(t)

			if outCounter==0:
				t.setVisible(False)

			sn_smallSys.yaw(math.pi/2.0)
			sn_smallSys.setScale(0.00001, 0.00001, 0.00001) #scale for panels - flat to screen

			hLoc = (8-col) + 1.5
			degreeConvert = 0.2*math.pi # 36 degrees per column
			sn_smallTrans.setPosition(Vector3(math.sin(hLoc*degreeConvert)*caveRadius, (7-row) * 0.29 + 0.41, math.cos(hLoc*degreeConvert)*caveRadius))
			sn_smallTrans.yaw(hLoc*degreeConvert)

			sn_smallMulti.addChild(sn_smallTrans)

			smallCount += 1

initSmallMulti()

##############################################################################################################
# INIT 3D SOLAR SYSTEM

def addOrbit(orbit, thick):
	global g_changeDistCircles

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

	g_changeDistCircles.append(circle)

	return circle

def initCenter(verticalHeight):
	global g_rot
	global g_orbit
	global g_changeSize
	global g_changeSizeCenterText
	global g_changeDistCircles
	global g_changeDistCenterHab
	global g_changeDistCenterPlanets

	theSys = li_allSys[0]

	#global sn_centerSys

	sn_centerTrans = SceneNode.create('solarSystem')
	sn_centerSys.addChild(sn_centerTrans)

	## the star
	#model = StaticObject.create('defaultSphere')
	model = SphereShape.create(theSys._star._size*c_scaleCenter_size*g_scale_size*0.02, 4)
	#model.setScale(Vector3(theSys._star._size*c_scaleCenter_size*g_scale_size, theSys._star._size*c_scaleCenter_size*g_scale_size, theSys._star._size*c_scaleCenter_size*g_scale_size))
	g_changeSize.append(model)
	model.getMaterial().setProgram('textured')
	model.setEffect('textured -v emissive -d '+theSys._star._texture)

	# activePlanets[name] = model

	sunDot = StaticObject.create('defaultSphere')
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

	## rotation
	sn_rotCenter = SceneNode.create('rotCenter'+theSys._star._name)
	sn_rotCenter.setPosition(Vector3(0,0,0))
	sn_rotCenter.addChild(sn_planetCenter)

	#activeRotCenters[name] = rotCenter
	sn_centerTrans.addChild(sn_rotCenter)

	# addOrbit(theSystem[name][1]*orbitScaleFactor*userScaleFactor, 0, 0.01)

	# deal with labelling everything
	v = Text3D.create('fonts/helvetica.ttf', 1, theSys._star._name)
	if CAVE():
		#v.setFontResolution(120)
		v.setFontSize(g_ftszcave_center)
		#v.setFontSize(g_ftszcave*10)
	else:
		#v.setFontResolution(10)
		v.setFontSize(g_ftszdesk*10)
	v.setPosition(Vector3(0, 500, 0))
	#v.setFontResolution(120)

	#v.setFontSize(160)
	v.getMaterial().setDoubleFace(1)
	v.setFixedSize(True)
	v.setColor(Color('white'))
	sn_planetCenter.addChild(v)

	## the planets
	for p in theSys._star._children:
		model = StaticObject.create('defaultSphere')
		#model = SphereShape.create(p._size * c_scaleCenter_size * g_scale_size, 4)
		model.setPosition(Vector3(0.0, 0.0, -p._orbit*g_scale_dist*c_scaleCenter_dist))
		model.setScale(Vector3(p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size))
		g_changeSize.append(model)
		g_changeDistCenterPlanets.append(model)
		model.getMaterial().setProgram('textured')
		model.setEffect('textured -d '+p._texture)

		#activePlanets[name] = model

		#set up for planet name on top of planet
		sn_planetCenter = SceneNode.create('planetCenter'+theSys._name+p._name)

		# deal with the axial tilt of the sun & planets
		sn_tiltCenter = SceneNode.create('tiltCenter'+theSys._name+p._name)
		sn_planetCenter.addChild(sn_tiltCenter)
		sn_tiltCenter.addChild(model)
		sn_tiltCenter.roll(p._inc/180.0*math.pi)

		# deal with rotating the planets around the sun
		sn_rotCenter = SceneNode.create('rotCenter'+theSys._name+p._name)
		#sn_rotCenter.setPosition(Vector3(0,0,0))
		sn_rotCenter.addChild(sn_planetCenter)

		g_orbit.append((sn_rotCenter,p._year))
		g_rot.append((model,p._day))

		#print "!!:",g_orbit[len(g_orbit)-1]

		#activeRotCenters[name] = rotCenter
		sn_centerTrans.addChild(sn_rotCenter)

		circle = addOrbit(p._orbit*g_scale_dist*c_scaleCenter_dist, 0.01)
		sn_centerTrans.addChild(circle)

		# deal with labelling everything
		v = Text3D.create('fonts/helvetica.ttf', 1, p._name)
		if CAVE():
			#v.setFontResolution(120)
			v.setFontSize(g_ftszcave_center)
			#v.setFontSize(g_ftszcave*10)
		else:
			#v.setFontResolution(10)
			v.setFontSize(g_ftszdesk*10)
		v.setPosition(Vector3(0, p._size*c_scaleCenter_size*g_scale_size, -p._orbit*c_scaleCenter_dist*g_scale_dist))
		g_changeSizeCenterText.append(v)
		g_changeDistCenterPlanets.append(v)
		#v.setFontResolution(120)

		v.getMaterial().setDoubleFace(1)
		v.setFixedSize(True)
		v.setColor(Color('white'))
		sn_planetCenter.addChild(v)

	## deal with the habitable zone

	cs_inner = CylinderShape.create(1, theSys._star._habNear*c_scaleCenter_dist*g_scale_dist, theSys._star._habNear*c_scaleCenter_dist*g_scale_dist, 10, 128)
	cs_inner.setEffect('colored -e #ff000055')
	cs_inner.getMaterial().setTransparent(True)
	cs_inner.pitch(-math.pi*0.5)
	cs_inner.setScale(Vector3(1, 1, 1.0))

	cs_outer = CylinderShape.create(1, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, 10, 128)
	cs_outer.setEffect('colored -e #00ff0055')
	cs_outer.getMaterial().setTransparent(True)
	cs_outer.pitch(-math.pi*0.5)
	cs_outer.setScale(Vector3(1, 1, 0.1))

	sn_habZone = SceneNode.create('habZone'+str(theSys._name))
	sn_habZone.addChild(cs_outer)
	sn_habZone.addChild(cs_inner)

	sn_centerTrans.addChild(sn_habZone)

	#g_changeDistCenterHab.append(sn_habZone)
	g_changeDistCenterHab.append(cs_outer)
	g_changeDistCenterHab.append(cs_inner)

	sn_centerTrans.addChild(light1)

	## add everything to the sn_centerTrans node for scaling and default positioning
	sn_centerTrans.setScale(Vector3(c_scaleCenter_overall, c_scaleCenter_overall, c_scaleCenter_overall))
	sn_centerTrans.setPosition(Vector3(0, verticalHeight, -1.5))

	## end here

initCenter(0.8)

##############################################################################################################
# MAJOR FUNCTIONS

## move to reorder small multiples
def doReorder(where):
	global g_reorder_mNum

	if cmp(where,'left')==0:
	 	toNum = (g_reorder_mNum-c_row_on_wall)
	elif cmp(where,'right')==0:
		toNum = (g_reorder_mNum+c_row_on_wall)
	elif cmp(where,'up')==0:
		toNum = (g_reorder_mNum-c_col_on_wall)
	elif cmp(where,'down')==0:
		toNum = (g_reorder_mNum+c_col_on_wall)

	if toNum<0:
		toNum+=48 # TO DO: total number of small multiples
	elif toNum>47:
		toNum-=48 # TO DO: total number of small multiples

	toNode = li_sysOnWall[toNum]
	toPos = toNode.getPosition()
	toOri = toNode.getOrientation()
	toNode.setPosition(li_sysOnWall[g_reorder_mNum].getPosition())
	toNode.setOrientation(li_sysOnWall[g_reorder_mNum].getOrientation())
	fromNode.setPosition(toPos)
	fromNode.setOrientation(toOri)
	li_sysOnWall[g_reorder_mNum], li_sysOnWall[toNum] = li_sysOnWall[toNum], li_sysOnWall[g_reorder_mNum] # swap
	g_reorder_mNum = toNum

## change the scale factor, if failed return False
def changeScale(name, add):
	global g_scale_size
	global g_scale_dist
	global g_scale_time

	global sn_smallMulti
	global wallLimit

	## dist
	if cmp(name,'dist')==0:
		#print 'enter dist'
		if add: # +
			#print 'enter +'
			g_scale_dist+=0.25
			#print 'new dist:', g_scale_dist
			if g_scale_dist>5:
				#print '> 5, restore value and return'
				g_scale_dist-=-.25
				return False
			else: # rescale
				#print 'not > 5, applying change'
				#print len(g_changeDistCircles)

				################ CENTER ######
				for sn in g_changeDistCircles:
					s = sn.getScale()
					#print 'former:',s
					sn.setScale(s.x*(g_scale_dist)/(g_scale_dist-0.25), s.y, s.z*(g_scale_dist)/(g_scale_dist-0.25))
					#print 'now:   ',sn.getScale()
				for hab in g_changeDistCenterHab:
					s = hab.getScale()
					#print 'former:',s
					hab.setScale(s.x*(g_scale_dist)/(g_scale_dist-0.25), s.y*(g_scale_dist)/(g_scale_dist-0.25), s.z)
					#print 'now:   ',hab.getScale()
				for m in g_changeDistCenterPlanets:
					m.setPosition(m.getPosition()*(g_scale_dist)/(g_scale_dist-0.25))

				for sn in g_cen_changeDistCircles:
					s = sn.getScale()
					#print 'former:',s
					sn.setScale(s.x*(g_scale_dist)/(g_scale_dist-0.25), s.y, s.z*(g_scale_dist)/(g_scale_dist-0.25))
					#print 'now:   ',sn.getScale()
				for hab in g_cen_changeDistCenterHab:
					s = hab.getScale()
					#print 'former:',s
					hab.setScale(s.x*(g_scale_dist)/(g_scale_dist-0.25), s.y*(g_scale_dist)/(g_scale_dist-0.25), s.z)
					#print 'now:   ',hab.getScale()
				for m in g_cen_changeDistCenterPlanets:
					m.setPosition(m.getPosition()*()/(g_scale_dist-0.25))

				################# WALL ########
				wallLimit*=(g_scale_dist-0.25)/(g_scale_dist) # wallLimit will be smaller

				# not work, too slow
				#removeAllChildren(sn_smallMulti)
				#initSmallMulti()

				for i in xrange(sn_smallMulti.numChildren()):
						#print 'child:',i
					sn_smallTrans = sn_smallMulti.getChildByName('smallTrans'+str(i))
					sn_smallSys = sn_smallTrans.getChildByName('smallSys'+str(i))
						#print 'sn_smallSys:',sn_smallSys
						#print sn_smallSys.numChildren()
					bs_habi = sn_smallSys.getChildByName('habiParent'+str(i)).getChildByIndex(0)
						#print 'bs_habi:',bs_habi
					t = sn_smallTrans.getChildByName('indicatorParent'+str(i)).getChildByIndex(0)
					sn_planetParent = sn_smallSys.getChildByName('planetParent'+str(i))

					curSys = li_allSys[i%2] # TO DO: need to be changed, currently only have 2 systems...
					habInner = curSys._star._habNear
					habOuter = curSys._star._habFar

					if habInner < wallLimit:
						if habOuter > wallLimit:
							habOuter = wallLimit
						habCenter = (habOuter+habInner)/2.0
						#bs_habi.setScale(s.x,s.y,s.z*g_scale_dist/(g_scale_dist-0.25))
						bs_habi.setScale(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
						bs_habi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
						bs_habi.setVisible(True)
					else:
						bs_habi.setVisible(False)

					outCounter = 0
					for j in xrange(sn_planetParent.numChildren()):
						m = sn_planetParent.getChildByIndex(j)

						p = m.getPosition()
						orbit = (48000 - p.z)/c_scaleWall_dist/(g_scale_dist-0.25)
						m.setPosition(p.x, p.y, 48000-(48000-p.z)*(g_scale_dist)/(g_scale_dist-0.25))
						if orbit > wallLimit:
							outCounter+=1
							m.setVisible(False)
						else:
							m.setVisible(True)

					if outCounter>0:
						outCounter /= 2 # a model and a text should be considered as one
						t.setText(str(outCounter)+' more planets -->>')
						t.setVisible(True)
					else:
						t.setVisible(False)

				#print 'done'
				return True
		else: # -
			g_scale_dist-=0.25
			if g_scale_dist<0.25:
				g_scale_dist+=0.25
				return False
			else: # rescale
				################ CENTER ######
				for sn in g_changeDistCircles:
					s = sn.getScale()
					sn.setScale(s.x*(g_scale_dist)/(g_scale_dist+0.25), s.y, s.z*(g_scale_dist)/(g_scale_dist+0.25))
				for hab in g_changeDistCenterHab:
					s = hab.getScale()
					hab.setScale(s.x*(g_scale_dist)/(g_scale_dist+0.25), s.y*(g_scale_dist)/(g_scale_dist+0.25), s.z)
				for m in g_changeDistCenterPlanets:
					m.setPosition(m.getPosition()*(g_scale_dist)/(g_scale_dist+0.25))

				for sn in g_cen_changeDistCircles:
					s = sn.getScale()
					#print 'former:',s
					sn.setScale(s.x*(g_scale_dist)/(g_scale_dist+0.25), s.y, s.z*(g_scale_dist)/(g_scale_dist+0.25))
					#print 'now:   ',sn.getScale()
				for hab in g_cen_changeDistCenterHab:
					s = hab.getScale()
					#print 'former:',s
					hab.setScale(s.x*(g_scale_dist)/(g_scale_dist+0.25), s.y*(g_scale_dist)/(g_scale_dist+0.25), s.z)
					#print 'now:   ',hab.getScale()
				for m in g_cen_changeDistCenterPlanets:
					m.setPosition(m.getPosition()*(g_scale_dist)/(g_scale_dist+0.25))

				################# WALL ########
				wallLimit*=(g_scale_dist+0.25)/(g_scale_dist) # wallLimit will be smaller

				for i in xrange(sn_smallMulti.numChildren()):
						#print 'child:',i
					#sn_smallTrans = sn_smallMulti.getChildByIndex(i)
					sn_smallTrans = sn_smallMulti.getChildByName('smallTrans'+str(i))
					#sn_smallSys = sn_smallTrans.getChildByIndex(sn_smallTrans.numChildren()-1)
					sn_smallSys = sn_smallTrans.getChildByName('smallSys'+str(i))
						#print 'sn_smallSys:',sn_smallSys
						#print sn_smallSys.numChildren()
					#bs_habi = sn_smallSys.getChildByIndex(sn_smallSys.numChildren()-2)
					bs_habi = sn_smallSys.getChildByName('habiParent'+str(i)).getChildByIndex(0)
						#print 'bs_habi:',bs_habi
					#t = sn_smallTrans.getChildByIndex(3)
					t = sn_smallTrans.getChildByName('indicatorParent'+str(i)).getChildByIndex(0)
					sn_planetParent = sn_smallSys.getChildByName('planetParent'+str(i))

					curSys = li_allSys[i%2] # TO DO: need to be changed, currently only have 2 systems...
					habInner = curSys._star._habNear
					habOuter = curSys._star._habFar

					if habInner < wallLimit:
						if habOuter > wallLimit:
							habOuter = wallLimit
						habCenter = (habOuter+habInner)/2.0
						#bs_habi.setScale(s.x,s.y,s.z*g_scale_dist/(g_scale_dist-0.25))
						bs_habi.setScale(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
						bs_habi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
						bs_habi.setVisible(True)
					else:
						bs_habi.setVisible(False)

					outCounter = 0
					for j in xrange(sn_planetParent.numChildren()):
						m = sn_planetParent.getChildByIndex(j)

						p = m.getPosition()
						orbit = (48000 - p.z)/c_scaleWall_dist/(g_scale_dist+0.25)
						m.setPosition(p.x, p.y, 48000-(48000-p.z)*(g_scale_dist)/(g_scale_dist+0.25))
						if orbit > wallLimit:
							outCounter+=1
							m.setVisible(False)
						else:
							m.setVisible(True)

					if outCounter>0:
						outCounter /= 2 # a model and a text should be considered as one
						t.setText(str(outCounter)+' more planets -->>')
						t.setVisible(True)
					else:
						t.setVisible(False)

				#print 'done'
				return True

	## size
	elif cmp(name,'size')==0:
		#print 'enter size'
		if add: # +
			#print 'enter +'
			g_scale_size+=0.25
			#print 'new size:', g_scale_size
			if g_scale_size>5:
				#print '> 5, restore value and return'
				g_scale_size-=0.25
				return False
			else: # rescale
				#print 'not > 5, applying change'
				#print len(g_changeSize)

				################ BOTH ########
				for m in g_changeSize:
					#print 'model'
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size-0.25))
					#print 'size_changed +'
				################ CENTER ######
				for t in g_changeSizeCenterText:
					p = t.getPosition()
					#print 'old:',t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size-0.25), p.z)
					#print 'new:',t.getPosition()
				for m in g_cen_changeSize:
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size-0.25))
				for t in g_cen_changeSizeCenterText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size-0.25), p.z)
				################ WALL ########
				for t in g_changeSizeWallText:
					#print '++'
					p = t.getPosition()
					print 'old:',t.getPosition()
					t.setPosition(Vector3(p.x, p.y*(g_scale_size)/(g_scale_size-0.25), p.z))
					print 'new:',t.getPosition()
				return True
		else: # -
			#print 'enter -'
			g_scale_size-=0.25
			if g_scale_size<0.25:
				g_scale_size+=0.25
				return False
			else: # rescale
				################ BOTH ########
				for m in g_changeSize:
					#print 'model'
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size+0.25))
					#print 'size_changed +'
				################ CENTER ######
				for t in g_changeSizeCenterText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size+0.25), p.z)
				for m in g_cen_changeSize:
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size+0.25))
				for t in g_cen_changeSizeCenterText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size+0.25), p.z)
				################ WALL ########
				for t in g_changeSizeWallText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size+0.25), p.z)
				return True

	## time
	elif cmp(name,'time')==0:
		if add: # +
			g_scale_time*=2
			if g_scale_time>16:
				g_scale_time*=0.5
				return False
		else: # -
			g_scale_time*=0.5
			if g_scale_time<0.25:
				g_scale_time*=2
				return False

def addCenter(verticalHeight, theSys):
	global g_cen_rot
	global g_cen_orbit
	global g_cen_changeSize
	global g_cen_changeSizeCenterText
	global g_cen_changeDistCircles
	global g_cen_changeDistCenterHab
	global g_cen_changeDistCenterPlanets

	removeAllChildren(sn_cen_sys)
	sn_centerTrans = SceneNode.create('centerTrans'+theSys._name)
	sn_cen_sys.addChild(sn_centerTrans)

	g_cen_orbit = []
	g_cen_rot = []
	g_cen_changeSize = []
	g_cen_changeSizeCenterText = []
	g_cen_changeDistCircles = []
	g_cen_changeDistCenterHab = []
	g_cen_changeDistCenterPlanets = []

	## the star
	#model = StaticObject.create('defaultSphere')
	model = SphereShape.create(theSys._star._size*c_scaleCenter_size*g_scale_size*0.02, 4)
	#model.setScale(Vector3(theSys._star._size*c_scaleCenter_size*g_scale_size, theSys._star._size*c_scaleCenter_size*g_scale_size, theSys._star._size*c_scaleCenter_size*g_scale_size))
	g_cen_changeSize.append(model)
	model.getMaterial().setProgram('textured')
	model.setEffect('textured -v emissive -d '+theSys._star._texture)

	# activePlanets[name] = model

	sunDot = StaticObject.create('defaultSphere')
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

	## rotation
	sn_rotCenter = SceneNode.create('rotCenter'+theSys._star._name)
	sn_rotCenter.setPosition(Vector3(0,0,0))
	sn_rotCenter.addChild(sn_planetCenter)

	#activeRotCenters[name] = rotCenter
	sn_centerTrans.addChild(sn_rotCenter)

	# addOrbit(theSystem[name][1]*orbitScaleFactor*userScaleFactor, 0, 0.01)

	# deal with labelling everything
	v = Text3D.create('fonts/helvetica.ttf', 1, theSys._star._name)
	if CAVE():
		#v.setFontResolution(120)
		v.setFontSize(g_ftszcave_center)
		#v.setFontSize(g_ftszcave*10)
	else:
		#v.setFontResolution(10)
		v.setFontSize(g_ftszdesk*10)
	v.setPosition(Vector3(0, 500, 0))
	#v.setFontResolution(120)

	#v.setFontSize(160)
	v.getMaterial().setDoubleFace(1)
	v.setFixedSize(True)
	v.setColor(Color('white'))
	sn_planetCenter.addChild(v)

	## the planets
	for p in theSys._star._children:
		#model = StaticObject.create('defaultSphere')
		model = SphereShape.create(p._size * c_scaleCenter_size * g_scale_size, 4)
		model.setPosition(Vector3(0.0, 0.0, -p._orbit*g_scale_dist*c_scaleCenter_dist))
		#model.setScale(Vector3(p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size))
		g_cen_changeSize.append(model)
		g_cen_changeDistCenterPlanets.append(model)
		model.getMaterial().setProgram('textured')
		model.setEffect('textured -d '+p._texture)

		#activePlanets[name] = model

		#set up for planet name on top of planet
		sn_planetCenter = SceneNode.create('planetCenter'+theSys._name+p._name)

		# deal with the axial tilt of the sun & planets
		sn_tiltCenter = SceneNode.create('tiltCenter'+theSys._name+p._name)
		sn_planetCenter.addChild(sn_tiltCenter)
		sn_tiltCenter.addChild(model)
		sn_tiltCenter.roll(p._inc/180.0*math.pi)

		# deal with rotating the planets around the sun
		sn_rotCenter = SceneNode.create('rotCenter'+theSys._name+p._name)
		#sn_rotCenter.setPosition(Vector3(0,0,0))
		sn_rotCenter.addChild(sn_planetCenter)

		g_cen_orbit.append((sn_rotCenter,p._year))
		g_cen_rot.append((model,p._day))

		#print "!!:",g_orbit[len(g_orbit)-1]

		#activeRotCenters[name] = rotCenter
		sn_centerTrans.addChild(sn_rotCenter)

		circle = addOrbit(p._orbit*g_scale_dist*c_scaleCenter_dist, 0.01)
		sn_centerTrans.addChild(circle)

		# deal with labelling everything
		v = Text3D.create('fonts/helvetica.ttf', 1, p._name)
		if CAVE():
			#v.setFontResolution(120)
			v.setFontSize(g_ftszcave_center)
			#v.setFontSize(g_ftszcave)
		else:
			#v.setFontResolution(10)
			v.setFontSize(g_ftszdesk*10)
		v.setPosition(Vector3(0, p._size*c_scaleCenter_size*g_scale_size, -p._orbit*c_scaleCenter_dist*g_scale_dist))
		g_cen_changeSizeCenterText.append(v)
		g_cen_changeDistCenterPlanets.append(v)
		#v.setFontResolution(120)

		v.getMaterial().setDoubleFace(1)
		v.setFixedSize(True)
		v.setColor(Color('white'))
		sn_planetCenter.addChild(v)

	## deal with the habitable zone

	cs_inner = CylinderShape.create(1, theSys._star._habNear*c_scaleCenter_dist*g_scale_dist, theSys._star._habNear*c_scaleCenter_dist*g_scale_dist, 10, 128)
	cs_inner.setEffect('colored -e #ff000055')
	cs_inner.getMaterial().setTransparent(True)
	cs_inner.pitch(-math.pi*0.5)
	cs_inner.setScale(Vector3(1, 1, 1.0))

	cs_outer = CylinderShape.create(1, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, 10, 128)
	cs_outer.setEffect('colored -e #00ff0055')
	cs_outer.getMaterial().setTransparent(True)
	cs_outer.pitch(-math.pi*0.5)
	cs_outer.setScale(Vector3(1, 1, 0.1))

	sn_habZone = SceneNode.create('habZone'+str(theSys._name))
	sn_habZone.addChild(cs_outer)
	sn_habZone.addChild(cs_inner)

	sn_centerTrans.addChild(sn_habZone)

	#g_changeDistCenterHab.append(sn_habZone)
	g_cen_changeDistCenterHab.append(cs_outer)
	g_cen_changeDistCenterHab.append(cs_inner)

	sn_centerTrans.addChild(light1)

	## add everything to the sn_centerTrans node for scaling and default positioning
	sn_centerTrans.setScale(Vector3(c_scaleCenter_overall, c_scaleCenter_overall, c_scaleCenter_overall))
	sn_centerTrans.setPosition(Vector3(0, verticalHeight, -1.5))

	## end here

##############################################################################################################
# EVENT FUNCTION

def onEvent():
	global g_scale_size
	global g_scale_dist
	global g_scale_time

	global g_reorder
	global g_moveToCenter

	global pointer

	e = getEvent()

	## normal operations
	if g_reorder==0 and g_moveToCenter==0:

		if e.isButtonDown(EventFlags.ButtonLeft) or e.isKeyDown(ord('j')):
			#print 'start dist -'
			if not changeScale('dist',False):
				playSound(sd_warn, e.getPosition(), 1.0)
		elif e.isButtonDown(EventFlags.ButtonRight) or e.isKeyDown(ord('l')):
			#print 'start dist +'
			if not changeScale('dist',True):
				playSound(sd_warn, e.getPosition(), 1.0)
		elif e.isButtonDown(EventFlags.ButtonUp) or e.isKeyDown(ord('i')):
			#print 'start size +'
			if not changeScale('size',True):
				playSound(sd_warn, e.getPosition(), 1.0)
		elif e.isButtonDown(EventFlags.ButtonDown) or e.isKeyDown(ord('k')):
			#print 'start size -'
			if not changeScale('size',False):
				playSound(sd_warn, e.getPosition(), 1.0)
		elif e.isKeyDown(ord('u')): # TO DO: in cave
			print 'start time -'
			if not changeScale('time',False):
				playSound(sd_warn, e.getPosition(), 1.0)
		elif e.isKeyDown(ord('o')): # TO DO: in cave
			print 'start time +'
			if not changeScale('time',True):
				playSound(sd_warn, e.getPosition(), 1.0)

	## choose to reorder
	elif g_reorder==1:
		if e.isButtonDown(EventFlags.Button2) or e.isKeyDown(ord('m')):
			e.setProcessed()
			r = getRayFromEvent(e)
			if r[0]:
				querySceneRay(r[1],r[2],reorderCallback)
				g_reorder = 2
				playSound(sd_reo_selected, cam.getPosition(), 1.0)
		elif e.isButtonDown(EventFlags.Button3):
			e.setProcessed()
			g_reorder==0
			playSound(sd_reo_quit, cam.getPosition(), 1.0)


	## move to reorder
	elif g_reorder==2:
		## quit reorder mode
		if e.isButtonDown(EventFlags.Button2):
			g_reorder = 1
			playSound(sd_reo_done, cam.getPosition(), 1.0)
			e.setProcessed()
		## move selected small multiple around
		elif e.isButtonDown(EventFlags.ButtonLeft) or e.isKeyDown(ord('j')):
			doReorder('left')
		elif e.isButtonDown(EventFlags.ButtonRight) or e.isKeyDown(ord('l')):
			doReorder('right')
		elif e.isButtonDown(EventFlags.ButtonUp) or e.isKeyDown(ord('i')):
			doReorder('up')
		elif e.isButtonDown(EventFlags.ButtonDown) or e.isKeyDown(ord('k')):
			doReorder('down')

	## move to center
	elif g_moveToCenter==1:
		r = getRayFromEvent(e)
		for node in li_boxOnWall:
			hitData = hitNode(node, r[1], r[2])
			if hitData[0]:
				pointer.setPosition(hitData[1])
				if e.isButtonDown(EventFlags.Button2):
					e.setProcessed()
					playSound(sd_mtc_moving, cam.getPosition(), 1.0)
					addCenter(1.2,dic_allBox[node])
					pointer.setVisible(False)
					g_mveToCenter==0
				break



setEventFunction(onEvent)

##############################################################################################################
# UPDATE FUNCTION

def onUpdate(frame, t, dt):
	global g_orbit
	global g_rot
	global g_scale_time

	#pass
	# ALL THINGS IN 3D ROTATE AS TIME PASSES BY
	for o,y in g_orbit:
		#i[0].yaw(dt/40*g_scale_time*(1.0/i[1])
		o.yaw(dt/40*g_scale_time*(1.0/y))
	for o,d in g_rot:
		#i[0].yaw(dt/40*g_scale_time*365*(1.0/i[1]))
		o.yaw(dt/40*365*g_scale_time*(1.0/d))

	for o,y in g_cen_orbit:
		#i[0].yaw(dt/40*g_scale_time*(1.0/i[1])
		if y==0:
			continue
		o.yaw(dt/40*g_scale_time*(1.0/y))
	for o,d in g_cen_rot:
		#i[0].yaw(dt/40*g_scale_time*365*(1.0/i[1]))
		if d==0:
			continue
		o.yaw(dt/40*365*g_scale_time*(1.0/d))

setUpdateFunction(onUpdate)

##############################################################################################################
# UTILITITIES FUNCTIONS

## recursively get all inivisible nodes below this node
def getInvisChildren(node):
	global g_invisOnes

	if node.numChildren()>0:
		for i in xrange(node.numChildren()):
			getInvisChildren(node.getChildByIndex(i))
	if node.isVisible()==False:
		g_invisOnes.append(node)

def toggleWallVisible():
	global sn_smallMulti
	global g_invisOnes

	global btn_hideWall

	if sn_smallMulti.isVisible(): # hide
		#print 'hiding everything on wall'
		getInvisChildren(sn_smallMulti)
		#print '# of nodes invisible:', len(g_invisOnes)
		sn_smallMulti.setChildrenVisible(False)
		sn_smallMulti.setVisible(False)
		#print 'hiding done'
		btn_hideWall.setText('show small multiples')
	else: # show
		#print 'recovering everything on wall'
		sn_smallMulti.setChildrenVisible(True)
		sn_smallMulti.setVisible(True)
		#print '# of nodes invisible:',len(g_invisOnes)
		for node in g_invisOnes:
			node.setVisible(False)
		#print 'they are invis now'
		g_invisOnes = []
		#print 'recovering done'
		btn_hideWall.setText('hide small multiples')

def removeAllChildren(sn):
	if sn.numChildren()>0:
		for i in xrange(sn.numChildren()):
			sn.removeChildByIndex(0)

def resetWall():
	global sn_smallMulti

	removeAllChildren(sn_smallMulti)

	initSmallMulti()

def resetCenter():
	global sn_centerSys

	removeAllChildren(sn_centerSys)

	initCenter(1)

def resetEverything():
	global g_scale_time
	global g_scale_size
	global g_scale_dist
	global wallLimit

	g_scale_size = 1
	g_scale_dist = 1
	g_scale_time = 1

	g_orbit = []
	g_rot = []
	g_changeSize = []
	g_changeSizeCenterText = []
	g_changeDistCircles = []
	g_changeDistCenterHab = []
	g_changeDistCenterPlanets = []

	g_changeSizeWallText = []

	g_cen_orbit = []
	g_cen_rot = []
	g_cen_changeSize = []
	g_cen_changeSizeCenterText = []
	g_cen_changeDistCircles = []
	g_cen_changeDistCenterHab = []
	g_cen_changeDistCenterPlanets = []

	wallLimit = WALLLIMIT

	resetCenter()
	resetWall()

def startReorder():
	global g_reorder
	g_reorder = 1
	mm.getMainMenu().hide()
	print 'now in reorder mode'
	playSound(sd_reo_please,cam.getPosition(),1.0)

def reorderCallback(node, distance):
	global g_reorder_mNum
	# if this node is smallTrans
	# then record location of it
	# and change the box's color
	pos = node.getPosition()
	print 'pos:',pos
	g_reorder_mNum = posToNum()

def startMoveToCenter():
	global g_moveToCenter
	global pointer

	g_moveToCenter = 1
	pointer.setVisible(True)
	#print 'start moving to center'
	#print 'closing menu'
	mm.getMainMenu().hide()
	#print 'done'
	playSound(sd_mtc_please,cam.getPosition(),1.0)

def pointingCallback(node, distance):
	print 'yawing!'
	node.yaw(math.pi*0.2)

def moveToCenterCallback(node, distance):
	# if this node is smallTrans
	# then move it to center
	todo = 0

# THE END ####################################################################################################
