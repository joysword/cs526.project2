import omegaToolkit
import euclid
import math
from caveutil import *
from csv import reader

##############################################################################################################
# GLOBAL VARIABLES
g_changeSize = []

g_changeDistCircles = []
g_changeDistCenterPlanets = []
g_changeDistCenterHab = []

#g_changeDistWallPlanets = []
#g_changeDistWallHab = []
#g_changeDistWallText = []

g_orbit = []
g_rot = []

wallLimit = 247000000 # by default, everything closer than this numer can be shown

## constants
WALLLIMIT = 247000000 # wallLimit will change, WALLLIMIT won't

c_scaleWall_size = 0.2
c_scaleWall_dist = 0.0008

c_scaleCenter_size = 0.01
c_scaleCenter_dist = 0.000005
c_scaleCenter_overall = 0.00025

R_jupiter = 69911 # in KM
R_sun = 695500 # in KM

## global scale factors
g_scale_size = 1.0
g_scale_dist = 1.0
g_scale_time = 1.0

## font size
g_ftszdesk = 0.03
g_ftszcave = 0

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
g_c = {'name':0, 'star':1, 'size':2, 'distance':3, 'orbit':3, 'texture':4, 'rs':5, 'dec':6, 'app_mag':7, 'class':8, 'type':9, 'num':10, 'day':11, 'year':12, 'inc':13, 'detection':14}

## bolometric correction constant for calculating habitable zone
g_BC = {'B':-2.0,'A':-0.3,'F':-0.15,'G':-0.4,'K':-0.8,'M':-2.0}

def CAVE():
	return caveutil.isCAVE();

##############################################################################################################
# CLASSES
class planet:
	def __init__(self,size,texture,orbit,name,day,year,inc,detection):
		self._size = float(size) * R_jupiter # to KM
		self._texture = texture
		self._orbit = KM_from_AU(float(orbit)) # to KM
		self._name = name
		self._day = float(day)
		self._year = float(year)
		self._inc = float(inc)
		self._detection = detection
		#self._model = None

class star:
	def __init__(self,t,mv,size,n,dis,c,ty,num):
		self._texture = t
		self._mv = float(mv)
		#print 'mv:',mv
		#print 'slef._mv:',self._mv
		self._size = float(size) * R_sun
		self._name = n
		self._dis = float(dis) # TO DO: int?
		self._class = c
		self._type = ty
		self._numChildren = int(num)
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

## menu to change other things
#
#

## change the scale factor, if failed return False
def changeScale(name, add):
	global g_scale_size
	global g_scale_dist
	global g_scale_time

	global g_changeDistWall
	global g_changeDistCenter
	global g_changeSize

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

				################# WALL ########
				#for m in g_changeDistWallPlanets:
				#	p = m.getPosition()
				#	m.setPosition(p.x, p.y, 48000-(48000-p.z)*(g_scale_dist)/(g_scale_dist-0.25))

				wallLimit*=(g_scale_dist-0.25)/(g_scale_dist) # wallLimit will be smaller

				# not work, too slow
				#removeAllChildren(sn_smallMulti)
				#initSmallMulti()

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
						orbit = (48000 - p.z)/c_scaleWall_dist/(g_scale_dist-0.25)
						m.setPosition(p.x, p.y, 48000-(48000-p.z)*(g_scale_dist)/(g_scale_dist-0.25))
						m.setPosition(Vector3(0.0,0.0,48000 - orbit * c_scaleWall_dist * g_scale_dist))
						if orbit > wallLimit:
							outCounter+=1
							m.setVisible(False)
						else:
							m.setVisible(True)

					if outCounter>0:
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

				################# WALL ########
				# for m in g_changeDistWallPlanets:
				# 	p = m.getPosition()
				# 	m.setPosition(p.x, p.y, 48000-(48000-p.z)*(g_scale_dist)/(g_scale_dist+0.25))

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
						m.setPosition(Vector3(0.0,0.0,48000 - orbit * c_scaleWall_dist * g_scale_dist))
						if orbit > wallLimit:
							outCounter+=1
							m.setVisible(False)
						else:
							m.setVisible(True)

					if outCounter>0:
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
				for m in g_changeSize:
					#print 'model'
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size-0.25))
					#print 'size_changed +'
				return True
		else: # -
			#print 'enter -'
			g_scale_size-=0.25
			if g_scale_size<0.25:
				g_scale_size+=0.25
				return False
			else: # rescale
				for m in g_changeSize:
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size+0.25))
					#print 'size_changed -'
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

##############################################################################################################
# LOAD DATA FROM FILE

li_allSys = [];

atLine = 0
f = open('data_test.csv','rU')
lines = reader(f)
for p in lines:
	atLine+=1
	if (atLine == 1):
		continue
	#print 'line:',atLine
	#print p
	if int(p[g_c['star']])==1: # star
		# def __init__(self,t,mv,r,n,dis,c,ty,num):
		curStar = star(p[g_c['texture']], p[g_c['app_mag']], p[g_c['size']], p[g_c['name']], p[g_c['distance']], p[g_c['class']], p[g_c['type']], p[g_c['num']])
		curSys = plaSys(curStar,curStar._dis,curStar._name)
		li_allSys.append(curSys)

	else: # planet
		# def __init__(self,size,texture,orbit,name,day,year,inc,detection):
		curPla = planet(p[g_c['size']], p[g_c['texture']], p[g_c['orbit']], p[g_c['name']], p[g_c['day']], p[g_c['year']], p[g_c['inc']], p[g_c['detection']])
		curStar.addPlanet(curPla)

print 'number of systems generated:', len(li_allSys)

##############################################################################################################
# INITIALIZE SMALL MULTIPLES

def initSmallMulti():
	global g_sn_size
	global g_sn_orbit

	smallCount = 0

	for col in xrange(0, 9):

		# leave a 'hole' in the center of the cave to see the far planets through
		if col>=3 and col<=5:
			continue

		for row in xrange(0, 8):

			#print 'smallCount:',smallCount
			curSys = li_allSys[smallCount%2]

			sn_smallTrans = SceneNode.create('smallTrans'+str(smallCount))

			bs_outlineBox = BoxShape.create(2.0, 0.25, 0.001)
			bs_outlineBox.setPosition(Vector3(-0.5, 0, 0.01))
			bs_outlineBox.setEffect('colored -e #01b2f144')
			bs_outlineBox.getMaterial().setTransparent(True)

			sn_smallSys = SceneNode.create('smallSys'+str(smallCount))

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
				#bs_habi = BoxShape.create(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
				# bs_habi = BoxShape.create(1, 1, 1)
				# bs_habi.setScale(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
				# bs_habi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
				# bs_habi.setEffect('colored -e #00611055')
				# bs_habi.getMaterial().setTransparent(True)
			else:
				#bs_habi = BoxShape.create(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
				# bs_habi = BoxShape.create(1, 1, 1)
				# bs_habi.setScale(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
				# bs_habi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
				# bs_habi.setEffect('colored -e #00611055')
				# bs_habi.getMaterial().setTransparent(True)
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
				if p._orbit > wallLimit:
					outCounter+=1
					model.setVisible(False)

			sn_smallSys.addChild(sn_planetParent)

			## get text
			t = Text3D.create('fonts/helvetica.ttf', 1, curSys._name + ' - ' + curSys._star._type + ' - ' + str(curSys._star._dis) + ' (ly)')
			if CAVE():
				t.setFontResolution(120)
			else:
				#t.setFontResolution(10)
				t.setFontSize(g_ftszdesk)
			t.setPosition(Vector3(0.3, 0.08, -0.05))
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

			t = Text3D.create('fonts/helvetica.ttf', 1, str(outCounter)+' more planets -->>')
			if CAVE():
				t.setFontResolution(120)
			else:
				#t.setFontResolution(10)
				t.setFontSize(g_ftszdesk)
			t.setPosition(Vector3(-0.9, 0.08, -0.05))
			t.yaw(math.pi) # back to face, face to back
			#t.setFontResolution(120)
			#t.getMaterial().setDoubleFace(1)
			t.getMaterial().setTransparent(False)
			t.getMaterial().setDepthTestEnabled(False)
			#t.setFixedSize(True)
			t.setColor(Color('white'))
				#sn_smallTrans.addChild(t)
			sn_smallTrans.addChild(sn_indicatorParent)
			sn_indicatorParent.addChild(t)

			if outCounter==0:
				t.setVisible(False)

			sn_smallSys.yaw(math.pi/2.0)
			sn_smallSys.setScale(0.00001, 0.00001, 0.00001) #scale for panels - flat to screen

			hLoc = col + 0.5
			degreeConvert = 36.0/360.0*2*math.pi #18 degrees per panel times 2 panels per viz = 36
			caveRadius = 3.25
			sn_smallTrans.setPosition(Vector3(math.sin(hLoc*degreeConvert)*caveRadius, row * 0.29 + 0.41, math.cos(hLoc*degreeConvert)*caveRadius))
			sn_smallTrans.yaw(hLoc*degreeConvert)

			sn_smallMulti.addChild(sn_smallTrans)

			smallCount += 1

initSmallMulti()

##############################################################################################################
# INIT 3D SOLAR SYSTEM

def addOrbit(orbit, thick, sn_centerTrans):
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

	g_changeDistCircles.append(circle)

def initCenter(verticalHeight, theSys):
	global g_rot
	global g_orbit

	#global sn_centerSys

	sn_centerTrans = SceneNode.create('centerTrans'+theSys._name)
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
		v.setFontResolution(120)
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
	g_orbit = []
	g_rot = []
	for p in theSys._star._children:
		#model = StaticObject.create('defaultSphere')
		model = SphereShape.create(p._size * c_scaleCenter_size * g_scale_size, 4)
		model.setPosition(Vector3(0.0, 0.0, -p._orbit*g_scale_dist*c_scaleCenter_dist))
		#model.setScale(Vector3(p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size))
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

		addOrbit(p._orbit*g_scale_dist*c_scaleCenter_dist, 0.01, sn_centerTrans)

		# deal with labelling everything
		v = Text3D.create('fonts/helvetica.ttf', 1, p._name)
		if CAVE():
			v.setFontResolution(120)
		else:
			#v.setFontResolution(10)
			v.setFontSize(g_ftszdesk*10)
		#v.setPosition(Vector3(0, p._orbit*c_scaleCenter_dist*g_scale_dist, - p._orbit*c_scaleCenter_dist*g_scale_dist))
		v.setPosition(Vector3(0.0, 0.0, 0.0))
		#v.setFontResolution(120)

		#v.setFontSize(160)
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

	sn_habZone = SceneNode.create('habZone')
	sn_habZone.addChild(cs_outer)
	sn_habZone.addChild(cs_inner)

	sn_centerTrans.addChild(sn_habZone)

	#g_changeDistCenterHab.append(sn_habZone)
	g_changeDistCenterHab.append(cs_outer)
	g_changeDistCenterHab.append(cs_inner)

	sn_centerTrans.addChild(light1)

	## add everything to the sn_centerTrans node for scaling and default positioning
	sn_centerTrans.setScale(Vector3(c_scaleCenter_overall, c_scaleCenter_overall, c_scaleCenter_overall))
	sn_centerTrans.setPosition(Vector3(0, verticalHeight, -2))

	## end here

initCenter(1.5, li_allSys[0])

##############################################################################################################
# EVENT FUNCTION

def onEvent():
	global g_scale_size
	global g_scale_dist
	global g_scale_time

	e = getEvent()

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
	elif e.isKeyDown(ord('u')):
		print 'start time -'
		if not changeScale('time',False):
			playSound(sd_warn, e.getPosition(), 1.0)
	elif e.isKeyDown(ord('o')):
		print 'start time +'
		if not changeScale('time',True):
			playSound(sd_warn, e.getPosition(), 1.0)

	## reset the scene
	elif e.isButtonDown(EventFlags.Button5) or e.isKeyDown(ord('r')):
		resetEverything()

	# elif e. isButtonDown(EventFlags.Button5):
	# 	if not changeScale('time',False):
	# 		playSound(sd_warn, e.getPosition(), 1.0)

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

setUpdateFunction(onUpdate)

##############################################################################################################
# UTILITITIES FUNCTIONS

def removeAllChildren(sn):
	for i in range(sn.numChildren()):
		sn.removeChildByIndex(0)

def resetWall():
	global sn_smallMulti

	removeAllChildren(sn_smallMulti)

	initSmallMulti()

def resetCenter():
	global sn_centerSys

	removeAllChildren(sn_centerSys)

	initCenter(1.5, li_allSys[0])

def resetEverything():
	global g_scale_time
	global g_scale_size
	global g_scale_dist
	global wallLimit

	g_scale_size = 1
	g_scale_dist = 1
	g_scale_time = 1
	wallLimit = WALLLIMIT

	resetCenter()
	resetWall()



# THE END ####################################################################################################
