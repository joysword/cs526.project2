import omegaToolkit
import euclid


##############################################################################################################
# GLOBAL VARIABLES
def enum(**enums):
    return type('Enum', (), enums)

starTy = enum()
planetTy = enum()

g_scale_size = 1
g_scale_dist = 1

##############################################################################################################
# CLASSES
class star:
	_texture = ''
	_radius = 0
	_name = 'star'
	_type = starTy.xx
	_numChildren = 0
	_habNear = 0
	_habFar = 0

	def __init__(t,r,n,ty,num):
		_texture = t
		_radius = r
		_name = n
		_type = ty
		_numChildren = num
		_habNear, _habFar = self.getHabZone(r)

	def getHabZone(r):
		near = r*10
		far = r*20
		return near, far

class planet:
	_texture = ''
	_radius = 0
	_name = 'planet'
	_type = planetTy.yy
	_day = 1 # a day of this planet is how many days in earth
	_year = 365 #  a year of this planet is how many days in earth
	_dist = 0

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
scaleSizeLabel.setText('size:')

scaleSizeBtnContainer = Container.create(ContainerLayout.LayoutVertical, scaleContainer)
scaleSizeBtnContainer.setPadding(-4)

scaleSizeUpBtn = Button.create(scaleSizeBtnContainer)
scaleSizeUpBtn.setText("+")
scaleSizeUpBtn.setUIEventCommand('changeScale("size", True)')

scaleSizeDownBtn = Button.create(scaleBtnContainer)
scaleSizeDownBtn.setText("-")
scaleSizeDownBtn.setUIEventCommand('changeScale("size", False)')

scaleDistLabel = Label.create(scaleContainer)
scaleDistLabel.setText('distance:')

scaleDistBtnContainer = Container.create(ContainerLayout.LayoutVertical, scaleContainer)
scaleDistBtnContainer.setPadding(-4)

scaleDistUpBtn = Button.create(scaleDistBtnContainer)
scaleDistUpBtn.setText('<')
scaleDistUpBtn.setUIEventCommand('changeScale("dist", False)')

scaleDistDownBtn = Button.create(scaleBtnContainer)
scaleDistDownBtn.setText('>')
scaleDistDownBtn.setUIEventCommand('changeScale("dist", True)')

## menu to change other things
#
#

## change the scale factor, if failed return False
def changeScale(name, add):
	global g_scale_size
	global g_scale_dist

	if cmp(name,'dist')==0:
		if add:
			g_scale=g_scale+0.25
			if g_scale>5:
				g_scale=5
				return False
		else:
			g_scale=g_scale-0.25
			if g_scale<0.25:
				g_scale=0.25
				return False
	return True

##############################################################################################################
# EVENT AND UPDATE FUNCTIONS
def onEvent():
	e = getEvent()

	if e.isButtonDown(EventFlags.ButtonLeft):
		if not changeScale('dist',False):
			playSound(sd_warn, e.getPosition(), 1.0)
	elif e.isButtonDown(EventFlags.ButtonRight):
		if not changeScale('dist',True):
			playSound(sd_warn, e.getPosition(), 1.0)
	if e.isButtonDown(EventFlags.ButtonUp):
		if not changeScale('size',True):
			playSound(sd_warn, e.getPosition(), 1.0)
	elif e.isButtonDown(EventFlags.ButtonDown):
		if not changeScale('size',False):
			playSound(sd_warn, e.getPosition(), 1.0)

setEventFunction(onEvent)
setUpdateFunction(onUpdate)

