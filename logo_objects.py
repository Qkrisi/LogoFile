from typing import Optional, Final
from copy import deepcopy

SETTINGS: Final[list[str]] = ['', 'aPos', 'xCor', 'yCor', 'pos', 'size', 'width', 'height', 'hint', 'enabled', '???', 'value', 'richText', 'font', 'colour', 'bgColour', 'editing', 'transparent', 'stayEditing', 'activePage', 'caption', 'caption', 'oneShot', 'style', 'down', 'allUp', 'flat', 'group', 'picture', '???', 'min', 'max', 'value', 'vertical', 'origin', 'bgLineColour', 'bgLineWidth', 'bgPicture', 'pageWho', 'bgColour', 'heading', 'homeState', 'xCor', 'yCor', 'fillColour', 'fillPattern', 'pen', 'penColour', 'penWidth', 'penPattern', 'rangeStyle', 'range', 'frame', 'shape', 'shapeScale', 'shapeColour', 'animation', 'font', 'transparentClick', 'parentHandle', 'fullPicture', 'voiceMenu', 'mainVoiceMenu', 'frameItem', 'autoDrag', 'sensitive', 'windowState', 'x', 'y', 'z', 'r', 'u', 'v', 'rangeX', 'rangeY', 'rangeZ', 'rangeR', 'rangeU', 'rangeV', 'deadZoneX', 'deadZoneY', 'deadZoneZ', 'deadZoneR', 'deadZoneU', 'deadZoneV', 'axesCount', 'buttonCount', 'pov', 'button1', 'button2', 'button3', 'button4', 'button5', 'button6', 'button7', 'button8', 'button9', 'button10', 'button11', 'button12', 'button13', 'button14', 'button15', 'button16', 'button17', 'button18', 'button19', 'button20', 'button21', 'button22', 'button23', 'button24', 'button25', 'button26', 'button27', 'button28', 'button29', 'button30', 'button31', 'button32', 'frameMode', 'bgColour', 'thumbLength', 'bgLinePattern', 'selection', 'selectedText', 'velocityXY', 'velocity', 'angle', 'prompt', 'readListPrompt', 'shownRange', '__name__', 'switch', 'useWho', 'transparent', 'fileName', 'showButtons', 'address', 'maximized', 'style', 'host', 'userID', 'port', 'attachments', 'body', 'fromAddress', 'fromName', 'replyTo', 'subject', 'toAddress', 'toBlindCarbonCopy', 'toCarbonCopy', 'showToolbar', 'server', 'delayScale', 'position', 'playState', 'style', 'port', 'controlledObject', 'align', 'order', 'caption', 'showTitleBar', 'caption', 'showTitleBar', 'maximized', 'style', 'runEnabled', 'nickName', '???', 'number', 'borderColour', 'acceptCommands', 'acceptKeyMenu', 'keyMenu', 'acceptVoiceMenu', 'frozen', 'userCanStop', 'growWithValue', 'oneLine', 'screenState', 'mainBarShown', 'paintbarShown', 'comname', 'port', 'baudrate', 'databits', 'stopbits', 'parity', 'RTSCTS', 'XONXOFF', 'asyncInput', 'connected']

class LogoSetting:
	def __init__(self, index: int, name: str):
		self.index: int = index
		self.name: str = name
		self.changed: bool = False

def LogoSettings(prefix: str, **settings):
	def inner(cls):
		cls._DEFAULTS: Final[dict[str, object]] = settings
		original = lambda self: None
		if hasattr(cls, "__init__"):
			original = getattr(cls, "__init__")
		def __init__(self, location):
			self._settings: dict[int, LogoSetting] = {}
			self._unknown: dict[int, object] = {}
			for key in settings:
				x: int = int(key[1:])
				setting: str = SETTINGS[x]
				self._settings[x] = LogoSetting(x, setting)
				setattr(self, setting, deepcopy(settings[key]))
			if self.__name__ == "":
				cls.count += 1
				self.name = f"{prefix}{cls.count}"
			original(self, location)
		setattr(cls, "__init__", __init__)
		return cls
	return inner

class LogoImage:
	#TODO implement this
	def __init__(self, size: int):
		self.size = size

@LogoSettings("obj", _132="", _176=[])
class Main:
	count = 0
	classlocation: "Main" = None
	classdefinitions: dict[str, str] = {}
	classevents: dict[str, str] = {}
	classownvars: dict[str, object] = {}
	classcommonvars: dict[str, object] = {}
	
	def __init__(self, location):
		self._initialize(location)
	
	def _initialize(self, location: Optional["Main"]):
		self.__location__ = location
		self.definitions: dict[str, str] = {}
		self.events: dict[str, str] = {}
		self.ownvars: dict[str, object] = {}
		self.commonvars: dict[str, object] = {}
	
	def _change(self, key: object, value, force: bool = False, record: bool = True):
		setting: str = SETTINGS[key] if isinstance(key, int) and 1 <= key and key < len(SETTINGS) else str(key)
		if setting == "???" or setting == "":
			self._unknown[key] = value
			return
		if hasattr(self, setting):
			setattr(self, setting, value)
			if record:
				self._settings[key].changed = True
		elif force or setting in self.ownvars:
			self.ownvars[setting] = value
		elif setting in self.commonvars:
			self.commonvars[setting] = value
		else:
			raise KeyError("Variable not found: " + setting)
		

@LogoSettings("", _1=[-4, 20], _4=[-4, 20], _5=[1928, 1064], _8="", _9=True, _19="alap", _20="", _21="", _62=[], _66=2, _129="? ", _130=": ", _132="fõablak", _163="", _165="", _166="", _173=[], _174=True, _175=True, _176=[], _177=True, _178=False, _182="osztottablak", _183=True, _184=False)
class MainWindow(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("lap", _5=[796, 499], _8="", _9=True, _15="fehér", _34=[398, 249], _35="fekete", _36=1, _37=LogoImage(1), _38=[], _39="fehér", _61=[], _121="fehér", _123=0, _132="", _176=[], _178=False)
class Page(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("p", _1=[398, 249], _4=[0, 0], _5=[100, 100], _8="", _9=True, _15="narancs11", _34=[50, 50], _35="fekete", _36=1, _37=LogoImage(1), _39="narancs11", _64=False, _121="narancs11", _123=0, _132="", _176=[], _178=False)
class Pane(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("eszközsor", _5=[1920, 34], _8="", _9=True, _132="", _161="felülre", _162=0, _176=[], _178=False)
class ToolBar(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("t", _1=[398, 249], _2=0, _3=0, _4=[0, 0], _8="", _13=[['System'], [0, 400, 0, 0, 0, 1]], _40=0, _41=[[0, 0], 0], _42=0, _43=0, _44="fekete", _45=0, _46="tollatle", _47="fekete", _48=1, _49=0, _50="körkörösablak", _51=[], _52=1, _53=LogoImage(24), _54=1, _55=[], _56=True, _57=[['System'], [0, 400, 0, 0, 0, 1]], _58=False, _63=1, _64=False, _65=False, _120=False, _131=[], _132="", _155=1, _176=[], _178=False)
class Turtle(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)
	
@LogoSettings("szd", _1=[398, 249], _4=[0, 0], _5=[100, 100], _8="", _9=True, _11="", _12=r"{\rtf1\ansi\ansicpg1252\deff0\deflang1033{\fonttbl{\f0\fnil\fcharset0 Tahoma;}}\r\n\viewkind4\uc1\pard\f0\fs16\par\r\n}", _13=[['Tahoma'], [8, 400, 0, 0, 0, 0]], _14="fekete", _15="fehér", _16=False, _17=False, _18=False, _32="", _39="fehér", _57=[['Tahoma'], [8, 400, 0, 0, 0, 0]], _121="fehér", _124=[0, 0], _125="", _132="", _135=False, _153=False, _176=[], _178=False, _180=True, _181=False)
class TextBox(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("cs", _1=[398, 249], _4=[0, 0], _5=[150, 23], _8="", _9=True, _11=0, _12="", _15=[245, 245, 245], _17=False, _30=0, _31=100, _32=0, _33=False, _39=[245, 245, 245], _121=[245, 245, 245], _122=18, _132="", _135=False, _176=[], _178=False)
class Slider(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("g", _1=[398, 249], _4=[0, 0], _5=[27, 28], _8="", _9=True, _12="", _20="g1", _21="g1", _23=0, _24=False, _25=True, _26=False, _27=0, _28=[], _60=False, _132="", _133=False, _134=True, _140=0, _158=0, _163="g1", _165="g1", _168=0, _176=[], _178=False, _179=True)
class Button(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("eszközgomb", _1=[398, 249], _4=[0, 0], _5=[27, 28], _8="", _9=True, _12="", _20="", _21="", _22=False, _23=0, _24=False, _26=False, _28=[], _60=False, _132="", _140=0, _158=0, _163="", _165="", _168=0, _176=[], _178=False)
class ToolButton(Button):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)
		for i in [20, 21, 163, 165]:
			self._change(i, self.name, False)

@LogoSettings("web", _1=[398, 249], _4=[0, 0], _5=[514, 370], _8="", _9=True, _12="", _20="", _21="", _23=0, _132="", _138="", _139=False, _140=0, _158=0, _163="", _164=False, _165="", _166=False, _167=False, _168=0, _176=[], _178=False)
class Web(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("médialejátszó", _1=[398, 249], _4=[0, 0], _5=[300, 245], _8="", _9=True, _20="", _21="", _23=0, _132="", _136="", _137=True, _139=False, _140=0, _156=0, _157="bezárt", _158=0, _163="", _164=False, _165="", _166=False, _167=False, _168=0, _176=[], _178=False)
class MediaPlayer(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("háló", _12="", _23="nincs", _132="", _140="nincs", _143=51, _154="", _158="nincs", _159=51, _168="nincs", _169=False, _170="nincs", _176=[], _186=51)
class Net(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("joy", _12="", _67=0, _68=0, _69=0, _70=0, _71=0, _72=0, _73=[0, 65535], _74=[0, 65535], _75=[0, 65535], _76=[0, 65535], _77=[0, 65535], _78=[0, 65535], _79=6553.5, _80=6553.5, _81=0, _82=0, _83=0, _84=0, _85=0, _86=0, _87=0, _88=False, _89=False, _90=False, _91=False, _92=False, _93=False, _94=False, _95=False, _96=False, _97=False, _98=False, _99=False, _100=False, _101=False, _102=False, _103=False, _104=False, _105=False, _106=False, _107=False, _108=False, _109=False, _110=False, _111=False, _112=False, _113=False, _114=False, _115=False, _116=False, _117=False, _118=False, _119=False, _126=[0, 0], _127=0, _128=90, _132="", _160=[], _172=1, _176=[])
class Joystick(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("port", _12="", _132="", _143="COM2", _159="COM2", _176=[], _186="COM2", _187=9600, _188=8, _189=1, _190=0, _191=1, _192=False, _193=False, _194=False)
class CommPort(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)

@LogoSettings("ole", _132="", _176=[], _185="")
class OleObject(Main):
	count = 0
	
	def __init__(self, location):
		self._initialize(location)
