import omegaToolkit
import euclid
import math
import pickle
from datetime import datetime
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

g_curOrder = [i for i in xrange(48)]

li_allSys = [] # classes, aaalllllll the systems
dic_allBox = {} # dictionary of small multiple boxes
dic_sys = {} # dictionary of systems
li_boxOnWall = [] # scenenodes (outlineBox)

li_textUniv = []

text_univ_highlight = None

# whether we are showing the info of a system
g_showInfo = False

wallLimit = 247000000 # by default, everything closer than this numer can be shown

## global scale factors
g_scale_size = 1.0
g_scale_dist = 1.0
g_scale_time = 1.0

## sets of systems
set_nearest = []
set_most_planets = []
set_farthest = []
set_g_type = []
set_save = [None]*48

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

c_scaleUniv_size = 0.000002

c_smallLabel_y_cave = 0.08

c_delta_scale = 0.2 # interval between each scale

R_jupiter = 69911 # in KM
R_sun = 695500 # in KM
M_earth = 5.97219e24 # in KG
R_earth = 6371 # in KM

dic_color = {'O':'#99ccf2', 'B':'#b2bfe6', 'A':'#e6e6fc', 'F':'#e6cc8c', 'G':'#ccb359', 'K':'#cc8059', 'M':'#cc1a0d'}

## font size
g_ftszdesk = 0.03
g_ftszcave = 0.03
g_ftszcave_center = 120

## for navigation
isButton7down = False
wandOldPos = Vector3()
wandOldOri = Quaternion()

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
g_c = {'sys':0 'name':1, 'star':2, 'size':3, 'distance':4, 'orbit':4, 'texture':5, 'ra':6, 'dec':7, 'app_mag':8, 'class':9, 'type':10, 'num':11, 'day':12, 'year':13, 'inc':14, 'detection':15, 'mass':16}

## bolometric correction constant for calculating habitable zone
g_BC = {'B':-2.0,'A':-0.3,'F':-0.15,'G':-0.4,'K':-0.8,'M':-2.0}

def CAVE():
	return caveutil.isCAVE();

##############################################################################################################
# CLASSES
class planet:
	def __getSizeFromMass(self, mass):
			#print 'mass:',mass
			if mass<5e25:
				return 0.5501*(mass**0.2858)*0.001 # to KM
			elif mass<1e27:
				return 7e-8*(mass**0.5609)*0.001 # to KM
			else:
				return 4e8*(mass**-0.0241)*0.001 # to KM

	def __init__(self,size,texture,orbit,name,day,year,inc,detection,mass):
		if cmp(size,'')==0:
			if cmp(mass,'')==0:
				self._mass = 0
				self._size = 0
			else:
				self._mass = float(mass) * M_earth
				self._size = self.__getSizeFromMass(self._mass)
				#print 'size:',self._size
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

		# if it is earth-sized
		if self._size<1.25*R_earth and self._size>0:
			self._isEarthSized = True
		else:
			self._isEarthSized = False

class star:
	def __init__(self,t,mv,size,n,dis,c,ty,num,ra,dec):
		self._texture = t

		if cmp(mv,'')==0:
			self._mv = 0
		else:
			self._mv = float(mv)

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

		self._ra = float(ra[0:2])*15 + float(ra[3:5])*0.25 + float(ra[6:])*0.004166
		self._dec = float(dec[1:3]) + float(dec[4:6])/60.0 + float(dec[7:])/3600.0
		if cmp(dec[0],'-')==0:
			self._dec *= -1.0

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
sd_reo_canceled = SoundInstance(sdEnv.loadSoundFromFile('reo_canceled','sound/reorder/canceled.wav'))

sd_mtc_please = SoundInstance(sdEnv.loadSoundFromFile('mtc_please','sound/movetocenter/please.wav'))
sd_mtc_moving = SoundInstance(sdEnv.loadSoundFromFile('mtc_moving','sound/movetocenter/moving.wav'))
sd_mtc_quit = SoundInstance(sdEnv.loadSoundFromFile('mtc_quit','sound/movetocenter/quit.wav'))

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
wgt_scale = menu_scale.addContainer()
container_scale = wgt_scale.getContainer()
container_scale.setLayout(ContainerLayout.LayoutHorizontal)
container_scale.setMargin(0)

lbl_scaleSize = Label.create(container_scale)
lbl_scaleSize.setText('size: ')

container_scaleSizeBtn = Container.create(ContainerLayout.LayoutVertical, container_scale)
container_scaleSizeBtn.setPadding(-4)

btn_scaleSizeUp = Button.create(container_scaleSizeBtn)
btn_scaleSizeUp.setText('+')
btn_scaleSizeUp.setUIEventCommand('changeScale("size", True)')

btn_scaleSizeDown = Button.create(container_scaleSizeBtn)
btn_scaleSizeDown.setText('-')
btn_scaleSizeDown.setUIEventCommand('changeScale("size", False)')

lbl_scaleDist = Label.create(container_scale)
lbl_scaleDist.setText('distance: ')

container_scaleDistBtn = Container.create(ContainerLayout.LayoutVertical, container_scale)
container_scaleDistBtn.setPadding(-4)

btn_scaleDistUp = Button.create(container_scaleDistBtn)
btn_scaleDistUp.setText('+')
btn_scaleDistUp.setUIEventCommand('changeScale("dist", True)')

btn_scaleDistDown = Button.create(container_scaleDistBtn)
btn_scaleDistDown.setText('-')
btn_scaleDistDown.setUIEventCommand('changeScale("dist", False)')

btn_scaleSizeUp.setHorizontalNextWidget(btn_scaleDistUp)
btn_scaleDistUp.setHorizontalPrevWidget(btn_scaleSizeUp)
btn_scaleSizeDown.setHorizontalNextWidget(btn_scaleDistDown)
btn_scaleDistDown.setHorizontalPrevWidget(btn_scaleSizeDown)

## menu to change time speed
menu_speed = mm.getMainMenu().addSubMenu('change time speed')
widget_speed = menu_speed.addContainer()
container_speed = widget_speed.getContainer()
container_speed.setLayout(ContainerLayout.LayoutHorizontal)
container_speed.setMargin(0)

lbl_speed = Label.create(container_speed)
lbl_speed.setText('time speed: ')

container_speedBtn = Container.create(ContainerLayout.LayoutVertical, container_speed)
container_speedBtn.setPadding(-4)

btn_speedUp = Button.create(container_speedBtn)
btn_speedUp.setText('+')
btn_speedUp.setUIEventCommand('changeScale("time", True)')

btn_speedDown = Button.create(container_speedBtn)
btn_speedDown.setText('-')
btn_speedDown.setUIEventCommand('changeScale("time", False)')

## menu to change to four predefined sets of system
menu_preset = mm.getMainMenu().addSubMenu('predefined set')

btn_nearest = menu_preset.addButton('system in smallest distance to us','loadPreset("near")')
btn_farthest = menu_preset.addButton('system in largest distance to us','loadPreset("far")')
btn_g_type = menu_preset.addButton('system with G type stars','loadPreset("g")')
btn_most_planets = menu_preset.addButton('system with most planets','loadPreset("most")')

## menu to filter small multiples
menu_filter = mm.getMainMenu().addSubMenu('filter small multiples')

menu_type = menu_filter.addSubMenu('type of star')
menu_dis = menu_filter.addSubMenu('distance to us')
menu_pla = menu_filter.addSubMenu('number of planets')

container_type = menu_type.getContainer() # TO DO : see if all these options have systems to show
btn_type_1 = Button.create(container_type)
btn_type_2 = Button.create(container_type)
btn_type_3 = Button.create(container_type)
btn_type_4 = Button.create(container_type)
btn_type_5 = Button.create(container_type)
btn_type_6 = Button.create(container_type)
btn_type_7 = Button.create(container_type)
btn_type_8 = Button.create(container_type)

btn_type_1.setText('O')
btn_type_2.setText('B')
btn_type_3.setText('A')
btn_type_4.setText('F')
btn_type_5.setText('G')
btn_type_6.setText('K')
btn_type_7.setText('M')
btn_type_8.setText('other')

btn_type_1.setCheckable(True)
btn_type_2.setCheckable(True)
btn_type_3.setCheckable(True)
btn_type_4.setCheckable(True)
btn_type_5.setCheckable(True)
btn_type_6.setCheckable(True)
btn_type_7.setCheckable(True)
btn_type_8.setCheckable(True)

btn_type_1.setChecked(True)
btn_type_2.setChecked(True)
btn_type_3.setChecked(True)
btn_type_4.setChecked(True)
btn_type_5.setChecked(True)
btn_type_6.setChecked(True)
btn_type_7.setChecked(True)
btn_type_8.setChecked(True)

container_dis = menu_dis.getContainer()
btn_dis_1 = Button.create(container_dis)
btn_dis_2 = Button.create(container_dis)
btn_dis_3 = Button.create(container_dis)
btn_dis_4 = Button.create(container_dis)

btn_dis_1.setText('0 - 100 ly')
btn_dis_2.setText('101 - 200 ly')
btn_dis_3.setText('200 - 1000 ly')
btn_dis_4.setText('>1000 ly')

btn_dis_1.setCheckable(True)
btn_dis_2.setCheckable(True)
btn_dis_3.setCheckable(True)
btn_dis_4.setCheckable(True)

btn_dis_1.setChecked(True)
btn_dis_2.setChecked(True)
btn_dis_3.setChecked(True)
btn_dis_4.setChecked(True)

container_pla = menu_pla.getContainer()
btn_pla_1 = Button.create(container_pla)
btn_pla_2 = Button.create(container_pla)
btn_pla_3 = Button.create(container_pla)
btn_pla_4 = Button.create(container_pla)
btn_pla_5 = Button.create(container_pla)
btn_pla_6 = Button.create(container_pla)
btn_pla_7 = Button.create(container_pla)

btn_pla_1.setText('2')
btn_pla_2.setText('3')
btn_pla_3.setText('4')
btn_pla_4.setText('5')
btn_pla_5.setText('6')
btn_pla_6.setText('7')
btn_pla_7.setText('8')

btn_pla_1.setCheckable(True)
btn_pla_2.setCheckable(True)
btn_pla_3.setCheckable(True)
btn_pla_4.setCheckable(True)
btn_pla_5.setCheckable(True)
btn_pla_6.setCheckable(True)
btn_pla_7.setCheckable(True)

btn_pla_1.setChecked(True)
btn_pla_2.setChecked(True)
btn_pla_3.setChecked(True)
btn_pla_4.setChecked(True)
btn_pla_5.setChecked(True)
btn_pla_6.setChecked(True)
btn_pla_7.setChecked(True)

btn_update = menu_filter.addButton('update','updateFilter()')

## menu to save and load configuration
menu_sl = mm.getMainMenu().addSubMenu('save/load configuration')

btn_save = menu_sl.addButton('save current configuration','saveConfig()')
menu_load = menu_sl.addSubMenu('load a configuration')

## button to show info image
btn_info = mm.getMainMenu().addButton('show info (beta)','showInfo()')

## button to move one of the small multiples to center
btn_moveToCenter = mm.getMainMenu().addButton('move to center','startMoveToCenter()')

## button to hide/show small multiples
btn_hideWall = mm.getMainMenu().addButton('hide small multiples','toggleWallVisible()')

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
sn_cen_sys = SceneNode.create('cen_sys') # another system in center
sn_smallMulti = SceneNode.create('smallMulti')
#sn_allSystems = SceneNode.create('allSystems')
sn_univTrans = SceneNode.create('univTrans')

sn_univParent = SceneNode.create('univParent')
sn_univTrans.addChild(sn_univParent)

sn_root.addChild(sn_centerSys)
sn_root.addChild(sn_smallMulti)
sn_root.addChild(sn_univTrans)
#sn_smallMulti.addChild(sn_allSystems)
sn_centerSys.addChild(sn_cen_sys)

# fix small multiples and 3d universe, no move
#if CAVE():
cam.addChild(sn_smallMulti)
cam.addChild(sn_univTrans)

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
#pointer.setEffect('colored -e #ff6600')
pointer.setVisible(False)

toggleStereo()

InitCamPos = cam.getPosition()
InitCamOri = cam.getOrientation()

if CAVE():
	cam.setControllerEnabled(False)
	cam.getController().setSpeed(0.15)

##############################################################################################################
# LOAD DATA FROM FILE

atLine = 0
f = open('data2.csv','rU')
lines = reader(f)
for p in lines:
	atLine+=1
	if (atLine == 1):
		continue
	#print 'line:',atLine
	#print p
	if int(p[g_c['star']])==1: # star
		# def __init__(self,t,mv,r,n,dis,c,ty,num):
		curStar = star(p[g_c['texture']], p[g_c['app_mag']], p[g_c['size']], p[g_c['name']], p[g_c['distance']], p[g_c['class']], p[g_c['type']], p[g_c['num']], p[g_c['ra']], p[g_c['dec']])

		curSys = plaSys(curStar,curStar._dis,curStar._name)
		li_allSys.append(curSys)

	else: # planet
		# def __init__(self,size,texture,orbit,name,day,year,inc,detection):
		curPla = planet(p[g_c['size']], p[g_c['texture']], p[g_c['orbit']], p[g_c['name']], p[g_c['day']], p[g_c['year']], p[g_c['inc']], p[g_c['detection']], p[g_c['mass']])
		curStar.addPlanet(curPla)

print 'number of systems generated:', len(li_allSys)

##############################################################################################################
# INITIALIZE PREDEFINED SETS

set_nearest = [i for i in xrange(len(li_allSys))]
#print 'nearest:'
#for i in xrange(50):
#	print set_nearest[i]
set_farthest = [(92-i) for i in xrange(len(li_allSys))]
set_farthest[0] = 0
#print 'farthest:'
#for i in xrange(50):
#	print set_farthest[i]
set_g_type = [0,1,5,6,10,12,14,18,19,20,21,23,24,28,29,32,33,34,35,36,37,39,41,43,44,45,47,48,50,53,54,56,57,58,59,60,61,62,63,64,65,67,68,69,70,72,73,75,79,80,82,87,88]
set_most_planets = [0,44,8,87,1,4,6,82,84,85,2,3,9,12,15,46,5,7,10,11,25,26,27,28,35,42,43,57,62,63,70,77,83,88,13,14,16,17,18,19,20,21,22,23,24,29,30,31,32,33,34,36,37,38,39,40,41,45,47,48,49,50,51,52,53,54,55,56,58,59,60,61,64,65,66,67,68,69,71,72,73,74,75,76,78,79,80,81,86,89,90,91]

##############################################################################################################
# INIT 3D UNIVERSE

def getPos(ra,dec,dis):
	x = dis*math.cos(dec)*math.cos(ra)
	y = dis*math.cos(dec)*math.sin(ra)
	z = dis*math.sin(dec)
	return Vector3(x,y,z)

def initUniv(preset):
	global sn_univParent
	global sn_univTrans
	global li_textUniv

	if sn_univParent.numChildren()>0:
		for i in xrange(sn_univParent.numChildren()):
			sn_univParent.removeChildByIndex(0)

	sn_univTrans.setPosition(1.2,1.8,-3)
	li_textUniv = []

	maxDis = 0
	for i in xrange(48):
		if preset[i]!=-1:
			curSys = li_allSys[preset[i]]
			if curSys._dis>maxDis:
				maxDis = curSys._dis

	for i in xrange(48):
		if preset[i]!=-1:
			curSys = li_allSys[preset[i]]
			star = SphereShape.create(math.sqrt(curSys._star._size * c_scaleUniv_size), 4)
			pos = getPos(curSys._star._ra, curSys._star._dec, curSys._star._dis)
			if maxDis>2000:
				pos = pos*1000/maxDis
			elif maxDis>1000:
				pos = pos*600/maxDis
			else:
				pos = pos*140/maxDis
			star.setPosition(pos)

			if curSys._star._class in dic_color.keys():
				#star.setEffect('colored -e '+dic_color[curSys._star._class])
				pass
			else:
				#star.setEffect('colored -e '+dic_color['G'])
				pass
			sn_univParent.addChild(star)

			t = Text3D.create('fonts/helvetica.ttf', 1, curSys._star._name)
			t.setFontSize(30)
			t.setFixedSize(True)
			t.setPosition(pos.x, pos.y+curSys._star._size * c_scaleUniv_size * 1.2, pos.z)
			t.setFacingCamera(cam)

			# sun text is in red
			if preset[i]==0:
				t.setColor(Color('red'))
			#caveutil.orientWithHead(cam,t)

			sn_univParent.addChild(t)
			li_textUniv.append(t)

	sn_univParent.setScale(0.005,0.005,0.005)

##############################################################################################################
# INITIALIZE SMALL MULTIPLES

def highlight(sys,star,p,t,size):
	if p._isEarthSized and p._orbit>star._habNear and p._orbit<star._habFar:
		t.setColor(Color('red'))
	elif cmp(sys._name, 'Gliese 876')==0 and cmp(p._name,'b')==0:
		t.setColor(Color('red'))
		if CAVE():
			t.setFontSize(size)
	elif cmp(sys._name,'55 Cancri')==0 and cmp(p._name,'f')==0:
		t.setColor(Color('red'))
		if CAVE():
			t.setFontSize(size)
	elif cmp(sys._name,'Upsilon Andromedae')==0 and cmp(p._name,'d')==0:
		t.setColor(Color('red'))
		if CAVE():
			t.setFontSize(size)
	elif cmp(sys._name,'47 Ursae Majoris')==0 and cmp(p._name,'b')==0:
		t.setColor(Color('red'))
		if CAVE():
			t.setFontSize(size)
	elif cmp(sys._name,'HD 37124')==0 and cmp(p._name,'c')==0:
		t.setColor(Color('red'))
		if CAVE():
			t.setFontSize(size)

def initSmallMulti(preset):

	global li_boxOnWall
	global dic_allBox
	global dic_sys

	global g_curOrder

	li_boxOnWall = []
	dic_allBox = {}
	dic_sys = {}

	# restore the order
	g_curOrder = [i for i in xrange(48)]

	smallCount = 0

	for col in xrange(0, 9):

		# leave a 'hole' in the center of the cave to see the far planets through
		if col>=3 and col<=5:
			continue

		for row in xrange(0, 8):

			sn_smallTrans = SceneNode.create('smallTrans'+str(smallCount))

			hLoc = (8-col) + 1.5
			degreeConvert = 0.2*math.pi # 36 degrees per column
			sn_smallTrans.setPosition(Vector3(math.sin(hLoc*degreeConvert)*caveRadius, (7-row) * 0.29 + 0.41, math.cos(hLoc*degreeConvert)*caveRadius))
			sn_smallTrans.yaw(hLoc*degreeConvert)
			sn_smallMulti.addChild(sn_smallTrans)

			sn_boxParent = SceneNode.create('boxParent'+str(smallCount))
			sn_smallTrans.addChild(sn_boxParent)

			bs_outlineBox = BoxShape.create(2.0, 0.25, 0.001)
			bs_outlineBox.setPosition(Vector3(-0.5, 0, 0.01))
			#bs_outlineBox.setEffect('colored -e #01b2f144')
			bs_outlineBox.getMaterial().setTransparent(True)
			sn_boxParent.addChild(bs_outlineBox)

			li_boxOnWall.append(bs_outlineBox)
			set_save[smallCount] = preset[smallCount]

			dic_allBox[bs_outlineBox] = None
			dic_sys[smallCount] = None

			if preset[smallCount]!=-1:
				curSys = li_allSys[preset[smallCount]]

				dic_allBox[bs_outlineBox] = curSys
				dic_sys[smallCount] = curSys

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
				else:
					habCenter = (habOuter+habInner)/2.0
					bs_habi.setVisible(False)

				bs_habi.setScale(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
				bs_habi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
				bs_habi.setEffect('colored -e #00611055')
				bs_habi.getMaterial().setTransparent(True)

				sn_smallSys.addChild(sn_habiParent)
				sn_habiParent.addChild(bs_habi)
					#sn_smallSys.addChild(bs_habi) # child 1

				sn_smallTrans.addChild(sn_smallSys)

				## get planets
				sn_planetParent = SceneNode.create('planetParent'+str(smallCount))

				outCounter = 0
				for p in curSys._star._children:
					model = StaticObject.create('defaultSphere')
					#model = SphereShape.create(p._size * c_scaleWall_size * g_scale_size, 4)
					model.setScale(Vector3(p._size * c_scaleWall_size * g_scale_size, p._size * c_scaleWall_size * g_scale_size, p._size * c_scaleWall_size * g_scale_size))
					model.setPosition(Vector3(0.0,0.0,48000 - p._orbit * c_scaleWall_dist * g_scale_dist))
					g_changeSize.append(model)
					print 'here'
					model.setEffect('textured -v emissive -d '+p._texture)
					print 'there'
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

					highlight(curSys,curSys._star,p,t,76)

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

			smallCount += 1

	initUniv(preset)

initSmallMulti(set_nearest)

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

		#circle.setEffect('colored -e white')

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
	model = StaticObject.create('defaultSphere')
	#model = SphereShape.create(theSys._star._size*c_scaleCenter_size*g_scale_size*0.02, 4)
	model.setScale(Vector3(theSys._star._size*c_scaleCenter_size*g_scale_size*0.02, theSys._star._size*c_scaleCenter_size*g_scale_size*0.02, theSys._star._size*c_scaleCenter_size*g_scale_size*0.02))
	model.setPosition(0,1000,0)
	g_changeSize.append(model)
	model.getMaterial().setProgram('textured')
	#model.setEffect('textured -v emissive -d '+theSys._star._texture)

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
	#sunLine.setEffect('colored -e white')
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
		#model.setEffect('textured -d '+p._texture)

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
	#cs_inner.setEffect('colored -e #000000')
	#cs_inner.getMaterial().setTransparent(True)
	cs_inner.getMaterial().setTransparent(False)
	cs_inner.pitch(-math.pi*0.5)
	cs_inner.setScale(Vector3(1, 1, 1.0))

	cs_outer = CylinderShape.create(1, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, 10, 128)
	#cs_outer.setEffect('colored -e #00ff0055')
	cs_outer.getMaterial().setTransparent(True)
	cs_outer.pitch(-math.pi*0.5)
	cs_outer.setScale(Vector3(1, 1, 0.08))

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
			old = g_scale_dist
			if old==0.001:
				g_scale_dist=0.005
			elif old==0.005:
				g_scale_dist=0.01
			elif old==0.01:
				g_scale_dist=0.05
			elif old==0.05:
				g_scale_dist=0.1
			elif old==0.1:
				g_scale_dist=0.2
			else:
				g_scale_dist+=c_delta_scale

			################ CENTER ######
			for sn in g_changeDistCircles:
				s = sn.getScale()
				#print 'former:',s
				sn.setScale(s.x*(g_scale_dist)/(old), s.y, s.z*(g_scale_dist)/(old))
				#print 'now:   ',sn.getScale()
			for hab in g_changeDistCenterHab:
				s = hab.getScale()
				#print 'former:',s
				hab.setScale(s.x*(g_scale_dist)/(old), s.y*(g_scale_dist)/(old), s.z)
				#print 'now:   ',hab.getScale()
			for m in g_changeDistCenterPlanets:
				m.setPosition(m.getPosition()*(g_scale_dist)/(old))

			for sn in g_cen_changeDistCircles:
				s = sn.getScale()
				#print 'former:',s
				sn.setScale(s.x*(g_scale_dist)/(old), s.y, s.z*(g_scale_dist)/(old))
				#print 'now:   ',sn.getScale()
			for hab in g_cen_changeDistCenterHab:
				s = hab.getScale()
				#print 'former:',s
				hab.setScale(s.x*(g_scale_dist)/(old), s.y*(g_scale_dist)/(old), s.z)
				#print 'now:   ',hab.getScale()
			for m in g_cen_changeDistCenterPlanets:
				m.setPosition(m.getPosition()*()/(old))

			################# WALL ########
			wallLimit*=(old)/(g_scale_dist) # wallLimit will be smaller

			# not work, too slow
			#removeAllChildren(sn_smallMulti)
			#initSmallMulti()

			for i in xrange(sn_smallMulti.numChildren()):
				sn_smallTrans = sn_smallMulti.getChildByName('smallTrans'+str(i))

				# if not an empty box
				if sn_smallTrans.numChildren()>1:
					sn_smallSys = sn_smallTrans.getChildByName('smallSys'+str(i))
					bs_habi = sn_smallSys.getChildByName('habiParent'+str(i)).getChildByIndex(0)
					t = sn_smallTrans.getChildByName('indicatorParent'+str(i)).getChildByIndex(0)
					sn_planetParent = sn_smallSys.getChildByName('planetParent'+str(i))

					#bs_outlineBox = sn_smallTrans.getChildByName('boxParent'+str(i)).getChildByIndex(0)

					#print 'bs_outlineBox:',bs_outlineBox
					curSys = dic_sys[i]
					#print 'curSys:',curSys
					#print 'pos:',bs_outlineBox.getPosition()
					habInner = curSys._star._habNear
					habOuter = curSys._star._habFar

					if habInner < wallLimit:
						if habOuter > wallLimit:
							habOuter = wallLimit
						habCenter = (habOuter+habInner)/2.0
						#bs_habi.setScale(s.x,s.y,s.z*g_scale_dist/(old))
						bs_habi.setScale(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
						bs_habi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
						bs_habi.setVisible(True)
					else:
						bs_habi.setVisible(False)

					outCounter = 0
					for j in xrange(sn_planetParent.numChildren()):
						m = sn_planetParent.getChildByIndex(j)

						p = m.getPosition()
						orbit = (48000 - p.z)/c_scaleWall_dist/(old)
						m.setPosition(p.x, p.y, 48000-(48000-p.z)*(g_scale_dist)/(old))
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

			return True
		else: # -
			old = g_scale_dist
			if old==0.001:
				return False
			elif old==0.005:
				g_scale_dist=0.001
			elif old==0.01:
				g_scale_dist=0.005
			elif old==0.05:
				g_scale_dist=0.01
			elif old==0.1:
				g_scale_dist=0.05
			elif old==0.2:
				g_scale_dist=0.1
			else:
				g_scale_dist-=c_delta_scale

			################ CENTER ######
			for sn in g_changeDistCircles:
				s = sn.getScale()
				sn.setScale(s.x*(g_scale_dist)/(old), s.y, s.z*(g_scale_dist)/(old))
			for hab in g_changeDistCenterHab:
				s = hab.getScale()
				hab.setScale(s.x*(g_scale_dist)/(old), s.y*(g_scale_dist)/(old), s.z)
			for m in g_changeDistCenterPlanets:
				m.setPosition(m.getPosition()*(g_scale_dist)/(old))

			for sn in g_cen_changeDistCircles:
				s = sn.getScale()
				#print 'former:',s
				sn.setScale(s.x*(g_scale_dist)/(old), s.y, s.z*(g_scale_dist)/(old))
				#print 'now:   ',sn.getScale()
			for hab in g_cen_changeDistCenterHab:
				s = hab.getScale()
				#print 'former:',s
				hab.setScale(s.x*(g_scale_dist)/(old), s.y*(g_scale_dist)/(old), s.z)
				#print 'now:   ',hab.getScale()
			for m in g_cen_changeDistCenterPlanets:
				m.setPosition(m.getPosition()*(g_scale_dist)/(old))

			################# WALL ########
			wallLimit*=(old)/(g_scale_dist) # wallLimit will be smaller

			for i in xrange(sn_smallMulti.numChildren()):
				sn_smallTrans = sn_smallMulti.getChildByName('smallTrans'+str(i))

				if sn_smallTrans.numChildren()>1:
					sn_smallSys = sn_smallTrans.getChildByName('smallSys'+str(i))
					bs_habi = sn_smallSys.getChildByName('habiParent'+str(i)).getChildByIndex(0)
					t = sn_smallTrans.getChildByName('indicatorParent'+str(i)).getChildByIndex(0)
					sn_planetParent = sn_smallSys.getChildByName('planetParent'+str(i))

					curSys = dic_sys[i]
					habInner = curSys._star._habNear
					habOuter = curSys._star._habFar

					if habInner < wallLimit:
						if habOuter > wallLimit:
							habOuter = wallLimit
						habCenter = (habOuter+habInner)/2.0
						#bs_habi.setScale(s.x,s.y,s.z*g_scale_dist/(old))
						bs_habi.setScale(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
						bs_habi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
						bs_habi.setVisible(True)
					else:
						bs_habi.setVisible(False)

					outCounter = 0
					for j in xrange(sn_planetParent.numChildren()):
						m = sn_planetParent.getChildByIndex(j)

						p = m.getPosition()
						orbit = (48000 - p.z)/c_scaleWall_dist/(old)
						m.setPosition(p.x, p.y, 48000-(48000-p.z)*(g_scale_dist)/(old))
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
			g_scale_size+=c_delta_scale
			#print 'new size:', g_scale_size
			if g_scale_size>30:
				#print '> 5, restore value and return'
				g_scale_size-=c_delta_scale
				return False
			else: # rescale
				#print 'not > 5, applying change'
				#print len(g_changeSize)

				################ BOTH ########
				for m in g_changeSize:
					#print 'model'
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size-c_delta_scale))
					#print 'size_changed +'
				################ CENTER ######
				for t in g_changeSizeCenterText:
					p = t.getPosition()
					#print 'old:',t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size-c_delta_scale), p.z)
					#print 'new:',t.getPosition()
				for m in g_cen_changeSize:
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size-c_delta_scale))
				for t in g_cen_changeSizeCenterText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size-c_delta_scale), p.z)
				################ WALL ########
				for t in g_changeSizeWallText:
					#print '++'
					p = t.getPosition()
					#print 'old:',t.getPosition()
					t.setPosition(Vector3(p.x, p.y*(g_scale_size)/(g_scale_size-c_delta_scale), p.z))
					#print 'new:',t.getPosition()
				return True
		else: # -
			#print 'enter -'
			g_scale_size-=c_delta_scale
			if g_scale_size<c_delta_scale:
				g_scale_size+=c_delta_scale
				return False
			else: # rescale
				################ BOTH ########
				for m in g_changeSize:
					#print 'model'
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size+c_delta_scale))
					#print 'size_changed +'
				################ CENTER ######
				for t in g_changeSizeCenterText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size+c_delta_scale), p.z)
				for m in g_cen_changeSize:
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size+c_delta_scale))
				for t in g_cen_changeSizeCenterText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size+c_delta_scale), p.z)
				################ WALL ########
				for t in g_changeSizeWallText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size+c_delta_scale), p.z)
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
	model = StaticObject.create('defaultSphere')
	#model = SphereShape.create(theSys._star._size*c_scaleCenter_size*g_scale_size*0.02, 4)
	model.setScale(Vector3(theSys._star._size*c_scaleCenter_size*g_scale_size*0.02, theSys._star._size*c_scaleCenter_size*g_scale_size*0.02, theSys._star._size*c_scaleCenter_size*g_scale_size*0.02))
	g_cen_changeSize.append(model)
	model.getMaterial().setProgram('textured')
	#model.setEffect('textured -v emissive -d '+theSys._star._texture)

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
	#sunLine.setEffect('colored -e white')
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
		model.setScale(Vector3(p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size))
		model.setPosition(Vector3(0.0, 0.0, -p._orbit*g_scale_dist*c_scaleCenter_dist))
		g_cen_changeSize.append(model)
		g_cen_changeDistCenterPlanets.append(model)
		model.getMaterial().setProgram('textured')
		#model.setEffect('textured -d '+p._texture)

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

		# highlight habitable candidates
		highlight(theSys,theSys._star,p,v,g_ftszcave_center*1.2)

	## deal with the habitable zone

	cs_inner = CylinderShape.create(1, theSys._star._habNear*c_scaleCenter_dist*g_scale_dist, theSys._star._habNear*c_scaleCenter_dist*g_scale_dist, 10, 128)
	#cs_inner.setEffect('colored -e #000000ff')
	#cs_inner.getMaterial().setTransparent(True)
	cs_inner.getMaterial().setTransparent(False)
	cs_inner.pitch(-math.pi*0.5)
	cs_inner.setScale(Vector3(1, 1, 1.0))

	cs_outer = CylinderShape.create(1, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, 10, 128)
	#cs_outer.setEffect('colored -e #00ff0055')
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

	global isButton7down
	global wandOldPos
	global wandOldOri

	global num_reorder
	global box_reorder

	global sn_smallMulti

	global li_textUniv

	global text_univ_highlight

	global g_curOrder

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
		elif e.isKeyDown(ord('u')):
			#print 'start time -'
			if not changeScale('time',False):
				playSound(sd_warn, e.getPosition(), 1.0)
		elif e.isKeyDown(ord('o')):
			#print 'start time +'
			if not changeScale('time',True):
				playSound(sd_warn, e.getPosition(), 1.0)

		## navigation
		elif (e.isButtonDown(EventFlags.Button7)):
			if isButton7down==False:
				isButton7down = True
				wandOldPos = e.getPosition()
				wandOldOri = e.getOrientation()
				#print "wandOldPos:",wandOldPos
				#print "wandOldOri:",wandOldOri
		elif (e.isButtonUp(EventFlags.Button7)):
			isButton7down = False
		elif e.getServiceType() == ServiceType.Wand:
			if isButton7down:
				#print 'button7isdown'
				trans = e.getPosition()-wandOldPos
				#cam.setPosition( cam.convertLocalToWorldPosition( trans*cam.getController().getSpeed() ) )
				cam.translate( trans*cam.getController().getSpeed(), Space.Local)
				oriVecOld = quaternionToEuler(wandOldOri)
				oriVec = quaternionToEuler(e.getOrientation())
				cam.rotate( oriVec-oriVecOld, 2*math.pi/180, Space.Local )

	## move to center
	elif g_moveToCenter==1:
		if e.isButtonDown(EventFlags.Button3):
			e.setProcessed()
			g_moveToCenter=0
			pointer.setVisible(False)
			playSound(sd_mtc_quit, cam.getPosition(), 1.0)
			print ('quit move to center mode')
		else:
			r = getRayFromEvent(e)
			for i in xrange(48):
				node = li_boxOnWall[i]
				hitData = hitNode(node, r[1], r[2])
				if hitData[0]:
					pointer.setPosition(hitData[1])
					if e.isButtonDown(EventFlags.Button2):
						e.setProcessed()
						if text_univ_highlight!=None:
							text_univ_highlight.setColor(Color('white'))
						li_textUniv[i].setColor(Color('red'))
						text_univ_highlight = li_textUniv[i]
						addCenter(1.2,dic_allBox[node])
						pointer.setVisible(False)
						g_moveToCenter=0
						playSound(sd_mtc_moving, cam.getPosition(), 1.0)
					break

	## choose to reorder
	elif g_reorder==1:
		# quit reorder mode
		if e.isButtonDown(EventFlags.Button3):
			e.setProcessed()
			g_reorder=0
			pointer.setVisible(False)
			playSound(sd_reo_quit, cam.getPosition(), 1.0)
			print 'quit reorder mode'
		else:
			r = getRayFromEvent(e)
			for i in xrange(sn_smallMulti.numChildren()):
				sn_smallTrans = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[i]))
				bs_outlineBox = sn_smallTrans.getChildByName('boxParent'+str(g_curOrder[i])).getChildByIndex(0)
				hitData = hitNode(bs_outlineBox, r[1], r[2])
				if hitData[0]:
					pointer.setPosition(hitData[1])
					# select a box
					if e.isButtonDown(EventFlags.Button2):
						#print 'button 2 clicked'
						e.setProcessed()
						g_reorder=2
						#print 'g_reoder=2'
						##bs_outlineBox.setEffect('colored -e #3274cc44') # change color to mark it
						#print 'box color changed'
						num_reorder = i # record this node's order
						box_reorder = bs_outlineBox # record this node
						##bs_outlineBox.setEffect('colored -e #01b2f144')
						playSound(sd_reo_selected, cam.getPosition(), 1.0)
					break

		# for node in li_boxOnWall:
		# 	hitData = hitNode(node, r[1], r[2])
		# 	if hitData[0]:
		# 		pointer.setPosition(hitData[1])
		# 		if e.isButtonDown(EventFlags.Button3):
		# 			e.setProcessed()
		# 			g_reorder=0
		# 			playSound(sd_reo_quit, cam.getPosition(), 1.0)
		# 		elif e.isButtonDown(EventFlags.Button2):
		# 			e.setProcessed()
		# 			g_reorder=2
		## 			node.setEffect('colored -e #3274cc44') # change color to mark it
		# 			box_reorder = node # record this node as reordering
		# 			playSound(sd_reo_selected, cam.getPosition(), 1.0)
		# 		break

	## move to reorder
	elif g_reorder==2:
		# cancel selection
		if e.isButtonDown(EventFlags.Button3):
			e.setProcessed()
			g_reorder=1
			##box_reorder.setEffect('colored -e #01b2f144') # restore original color
			playSound(sd_reo_canceled, cam.getPosition(), 1.0)
 			playSound(sd_reo_please, cam.getPosition(), 1.0)
 			print ('cenceled')
 		else:
			r = getRayFromEvent(e)
			for i in xrange(sn_smallMulti.numChildren()):
				sn_smallTrans = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[i]))
				bs_outlineBox = sn_smallTrans.getChildByName('boxParent'+str(g_curOrder[i])).getChildByIndex(0)
				hitData = hitNode(bs_outlineBox, r[1], r[2])
				if hitData[0]:
					pointer.setPosition(hitData[1])
			 		# select another box
			 		if e.isButtonDown(EventFlags.Button2):
			 			#for ii in xrange(sn_smallMulti.numChildren()):
			 			#	print ii,sn_smallMulti.getChildByIndex(ii)
			 			e.setProcessed()
			 			if i != num_reorder:
			 				##bs_outlineBox.setEffect('colored -e #3274cc44') # change color to mark it
			 				curPos = sn_smallTrans.getPosition()
			 				curOri = sn_smallTrans.getOrientation()
			 				if i<num_reorder:
			 					for j in xrange(i,num_reorder):
			 						n = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[j]))
			 						n1 = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[j+1]))
			 						n.setPosition(n1.getPosition())
			 						n.setOrientation(n1.getOrientation())
			 					n = sn_smallMulti.getChildByName('smallTrans'+str(num_reorder))
			 					n.setPosition(curPos)
			 					n.setOrientation(curOri)
			 					# update g_curOrder
			 					tmpNum = g_curOrder[num_reorder]
			 					j = num_reorder
		 						while j>i:
		 							g_curOrder[j]=g_curOrder[j-1]
		 							j-=1
		 						g_reorder[i]=tmpNum

			 				else:
			 					j = i
			 					while j>num_reorder:
			 						n = sn_smallMulti.getChildByName('smallTrans'+str(j))
			 						n1 = sn_smallMulti.getChildByName('smallTrans'+str(j-1))
			 						n.setPosition(n1.getPosition())
			 						n.setOrientation(n1.getOrientation())
			 						j-=1
			 					n = sn_smallMulti.getChildByName('smallTrans'+str(num_reorder))
			 					n.setPosition(curPos)
			 					n.setOrientation(curOri)
			 					#update g_curOrder
			 					tmpNum = g_curOrder[num_reorder]
			 					for j in xrange(num_reorder,i):
			 						g_curOrder[j]=g_curOrder[j+1]
			 					g_reorder[i]=tmpNum

			 				playSound(sd_reo_done, cam.getPosition(), 1.0)
			 				g_reorder=1
			 		break

		# for node in li_boxOnWall:
		# 	hitData = hitNode(node, r[1], r[2])
		# 	if hitData[0]:
		# 		pointer.setPosition(hitData[1])
		# 		if e.isButtonDown(EventFlags.Button3):
		# 			e.setProcessed()
		# 			g_reorder=1
		## 			box_reorder.setEffect('colored -e #01b2f144') # restore original color
		# 			playSound(sd_reo_canceled, cam.getPosition(), 1.0)
		# 			playSound(sd_reo_please, cam.getPosition(), 1.0)
		# 		elif e.isButtonDown(EventFlags.Button2):
		# 			if node != box_reorder:

		# 	break

setEventFunction(onEvent)

##############################################################################################################
# UPDATE FUNCTION

def onUpdate(frame, t, dt):
	global g_orbit
	global g_rot
	global g_scale_time

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

	# 3d universe
	sn_univParent.yaw(dt/20)

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

def resetWall(set_):
	global sn_smallMulti

	#print ('start removing all children of sn_smallMulti')
	removeAllChildren(sn_smallMulti)
	#print ('done removing')

	#print 'start initSmallMulti'
	initSmallMulti(set_)
	#print 'done resetting'

def resetCenter():
	global sn_centerSys

	removeAllChildren(sn_centerSys)

	initCenter(1)

def resetEverything():
	global g_scale_time
	global g_scale_size
	global g_scale_dist

	global g_orbit
	global g_rot
	global g_changeSize
	global g_changeSizeCenterText
	global g_changeDistCircles
	global g_changeDistCenterHab
	global g_changeDistCenterPlanets

	global g_changeSizeWallText

	global g_cen_orbit
	global g_cen_rot
	global g_cen_changeSize
	global g_cen_changeSizeCenterText
	global g_cen_changeDistCircles
	global g_cen_changeDistCenterHab
	global g_cen_changeDistCenterPlanets

	global wallLimit

	global g_reorder
	global g_moveToCenter
	global g_invisOnes

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

	g_reorder = 0
	g_moveToCenter = 0
	g_invisOnes = []

	cam.setPosition(InitCamPos)
	cam.setOrientation(InitCamOri)
	print 'initCamPos:',InitCamPos
	print 'initCamOri:',InitCamOri
	#cam.setPosition(Vector3(0,0,0))
	#cam.setOrientation(Quaternion(0,0,0,0))

	resetCenter()
	resetWall(set_nearest)

def startReorder():
	global g_reorder
	global pointer

	g_reorder = 1
	pointer.setVisible(True)
	mm.getMainMenu().hide()
	print 'now in reorder mode'
	playSound(sd_reo_please,cam.getPosition(),1.0)

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

def loadPreset(s):
	global sn_smallMulti

	if cmp(s,'near')==0:
		resetWall(set_nearest)
	elif cmp(s,'far')==0:
		resetWall(set_farthest)
	elif cmp(s,'g')==0:
		resetWall(set_g_type)
	elif cmp(s,'most')==0:
		resetWall(set_most_planets)
	else:
		resetWall(set_nearest)

def saveConfig():
	global menu_load
	global set_save

	print 'start saving'
	li = [None]*48
	t = datetime.now().strftime("%m-%d-%y %H:%M:%S")
	filename = t[0]+t[1]+t[3]+t[4]+t[6]+t[7]+t[9]+t[10]+t[12]+t[13]+t[15]+t[16]
	#print "time:",t
	print 'file:',filename
	with open(filename, 'w') as f:
		pickle.dump(set_save,f)
		#print 'f:'
		#print f
	#print 'saved to '+t
	menu_load.addButton(t,'loadConfig('+str(filename)+')')

def loadConfig(filename):
	global set_save
	global sn_smallMulti

	#print 'filename:', filename

	f = open(str(filename), 'r')

	#with open(filename, 'r') as f:
	set_save = pickle.load(f)
	resetWall(set_save)

def updateFilter():
	print 'start updating'
	res = []

	res.append(0)

	for i in xrange(1,len(li_allSys)):
		print 'testing system', i
		sys = li_allSys[i]

		## check type
		if cmp(sys._star._class,'O')==0:
			if btn_type_1.isChecked()==False:
				continue
		elif cmp(sys._star._class,'B')==0:
			if btn_type_2.isChecked()==False:
				continue
		elif cmp(sys._star._class,'A')==0:
			if btn_type_3.isChecked()==False:
				continue
		elif cmp(sys._star._class,'F')==0:
			if btn_type_4.isChecked()==False:
				continue
		elif cmp(sys._star._class,'G')==0:
			if btn_type_5.isChecked()==False:
				continue
		elif cmp(sys._star._class,'K')==0:
			if btn_type_6.isChecked()==False:
				continue
		elif cmp(sys._star._class,'M')==0:
			if btn_type_7.isChecked()==False:
				continue
		else:
			if btn_type_8.isChecked()==False:
				continue

		## check distance
		if sys._dis<=100:
			if btn_dis_1.isChecked()==False:
				continue
		elif sys._dis<=200:
			if btn_dis_2.isChecked()==False:
				continue
		elif sys._dis<=1000:
			if btn_dis_3.isChecked()==False:
				continue
		else:
			if btn_dis_4.isChecked()==False:
				continue

		## check number of planets
		if sys._star._numChildren==2:
			if btn_pla_1.isChecked()==False:
				continue
		elif sys._star._numChildren==3:
			if btn_pla_2.isChecked()==False:
				continue
		elif sys._star._numChildren==4:
			if btn_pla_3.isChecked()==False:
				continue
		elif sys._star._numChildren==5:
			if btn_pla_4.isChecked()==False:
				continue
		elif sys._star._numChildren==6:
			if btn_pla_5.isChecked()==False:
				continue
		elif sys._star._numChildren==7:
			if btn_pla_6.isChecked()==False:
				continue
		else:
			if btn_pla_7.isChecked()==False:
				continue

		#print 'need to add'
		res.append(i)
		#print 'added'

	#print 'done testing'
	if len(res)<48:
		#print 'added less then 48 systems, filling up using None'
		for i in xrange(len(res),48):
			res.append(-1)
		#print 'done filling up'
	#print 'start resetting the wall'
	resetWall(res)

def showInfo():
	global g_showInfo

	g_showInfo = True
	ui = UiModule.createAndInitialize()
	wf = ui.getWidgetFactory()
	uiroot = ui.getUi()

	legend = wf.createImage('legend', uiroot)
	legend.setData(loadImage('images/Tau_Ceti.png'))
	legend.setLayer(WidgetLayer.Front)
	#legend.setSize(Vector2(UIScale * 180, UIScale * 240))
	#yWidgPos = (UIScale * 480) - legend.getSize()[1]
	if CAVE():
		legend.setPosition(Vector2(15025 ,0))
	else:
		legend.setPosition(Vector2(0 ,0))
	print 'done loading image'
