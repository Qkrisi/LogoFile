from typing import Optional, List, Dict
from datetime import datetime
from copy import deepcopy
from lang import hungarian
import logo_objects as obj
import io
import os

_ENCODING = "ISO-8859-1"

_LOCALES = {
	"hungarian": hungarian
}

_ESCAPE = ['\\', ' ', '[', ']', '(', ')', '"', '+', '-', '/', '*', '|']

def _readint32(stream: io.BufferedIOBase) -> int:
	return int.from_bytes(stream.read(4), byteorder="little")

def _int32bytes(n: int) -> bytes:
	return n.to_bytes(4, byteorder="little")

def _readstr(stream: io.BufferedIOBase) -> str:
	s: str = ""
	while (b := stream.read(1)[0]) != 0x22:
		s += chr(b)
	return s

def _readint(length: int, stream: io.BufferedIOBase) -> int:
	n: int = 0
	for _ in range(length):
		n *= 10
		n += stream.read(1)[0] - 48
	return n

def _get_command_bytes(stream: io.BytesIO) -> Optional[bytes]:
	res: bytearray = bytearray()
	cont = True
	end: bool = False
	while True:
		b: bytes = stream.read(1)
		if b == b"":
			end = True
			break
		value: int = b[0]
		if value == 0x0A:	#\n
			cont = False
			continue
		elif value == 0x0D:	#\r
			if not cont:
				stream.read(1)
				break
			continue
		elif value == 0x09:	#\t
			value = 0x01
		elif not cont:
			stream.seek(-1, os.SEEK_CUR)
			break
		cont = True
		res += value.to_bytes(1)
	if end and len(res) == 0:
		return None
	return bytes(res)

def _parsevalue(value: bytearray, strlevel: int, inlist: bool) -> object:
	s: str = value.decode(_ENCODING)
	if strlevel > 0:
		return s
	if s == "igaz":
		return True
	if s == "hamis":
		return False
	try:
		return int(s)
	except ValueError:
		try:
			return float(s)
		except ValueError:
			return s if inlist else LogoCommandEval(s)

def _tostr(value: object, inlist: bool = False) -> str:
	if isinstance(value, bool):
		return "igaz" if value else "hamis"
	if isinstance(value, str):
		if "|" in value:
			for c in _ESCAPE:
				value = value.replace(c, "\\" + c)
			return value if inlist else '"' + value
		return f'|{value}|' if inlist else f'"|{value}|'
	if isinstance(value, int) or isinstance(value ,float):
		return str(value)
	if isinstance(value, list):
		s = "["
		tail = False
		for inner in value:
			if tail:
				s += " "
			tail = True
			s += _tostr(inner, True)
		s += "]"
		return s
	if isinstance(value, LogoCommandEval):
		return value.cmd
	raise TypeError(f"Unknown Imagine type: {type(value)}")

def _process_setting(key: str, value: object, locales, definitions: dict[str, str], events: dict[str, str], ownvars: dict[str, object], commonvars: dict[str, object]) -> bool:
	if key.startswith(locales.SETTING_SELFDEFINE):
		key = key.replace(locales.SETTING_SELFDEFINE, "", 1)
		if isinstance(value, list):
			newvalue: str = "eljárás " + key
			for p in value[0]:
				newvalue += " :" + p
			newvalue += chr(0xB6) + " " + _tostr(value[1]).replace("|", "") + chr(0xB6) + "vége"
			value = newvalue
		definitions[key] = value.replace(chr(0xB6), "\n")
		return True
	if key.startswith(locales.SETTING_EVENT):
		key = key.replace(locales.SETTING_EVENT, "", 1)
		events[key] = _tostr(value) if isinstance(value, list) else value
		return True
	if key.startswith(locales.SETTING_OWNVAR):
		key = key.replace(locales.SETTING_OWNVAR, "", 1)
		ownvars[key] = value
		return True
	if key.startswith(locales.SETTING_COMMONVAR):
		key = key.replace(locales.SETTING_COMMONVAR, "", 1)
		commonvars[key] = value
		return True
	return False

def _tolocation(o: obj.Main | type) -> str:
	current: obj.Main | type = o
	s: str = ""
	while current != None:
		if s != "":
			s = "'" + s
		s = current.__name__ + s
		current = current.__location__ if isinstance(o, obj.Main) else current.classlocation
	return s

class LogoCommandEval:
	def __init__(self, cmd: str):
		self.cmd: str = cmd

class LogoProjectSettings:
	def __init__(self, language: str, path: str, version: str, date: datetime):
		self.language: str = language
		self.path: str = path
		self.version: str = version
		self.date: datetime = date
		if self.language not in _LOCALES:
			raise ValueError("Unknown language: " + self.language)
		self._locales = _LOCALES[self.language]
	
	def read(stream: io.BufferedIOBase) -> "LogoProjectSettings":
		stream.read(11)	#language: "
		language: str = _readstr(stream)
		stream.read(8)	#_name: "
		path: str = _readstr(stream)
		stream.read(12)	#__version: "
		version: str = _readstr(stream)
		stream.read(8)	#__date:_
		datestr: str = stream.read(19).decode(_ENCODING)	#DD.MM.YYYY HH:MM:SS
		stream.read(4)	#\r\n\r\n
		return LogoProjectSettings(language, path, version, datetime.strptime(datestr, "%d.%m.%Y %H:%M:%S"))
	
	def __bytes__(self) -> bytes:
		res: bytearray = bytearray(b"\x6C\x61\x6E\x67\x75\x61\x67\x65\x3A\x20\x22")	#language: "
		res += self.language.encode(_ENCODING)
		res += b"\x22\x20\x6E\x61\x6D\x65\x3A\x20\x22"	#" name: "
		res += self.path.encode(_ENCODING)
		res += b"\x22\x20\x20\x76\x65\x72\x73\x69\x6F\x6E\x3A\x20\x22"	#"  version: "
		res += self.version.encode(_ENCODING)
		res += b"\x22\x20\x20\x64\x61\x74\x65\x3A\x20"	#"  date:_
		res += self.date.strftime("%d.%m.%Y %H:%M:%S").encode(_ENCODING)
		#res += b"\x0D\x0A\x0D\x0A"	#\r\n\r\n
		return bytes(res)
		

class LogoHeader:
	def __init__(self, version: int, graphicsnum: int, langoverride: bool, language: str = ""):
		self.version: int = version
		self.graphicsnum: int = graphicsnum
		self.size: int = 0
		self.langoverride: bool = langoverride
		if self.langoverride:
			self.language: str = language
			self.langsize: int = len(self.language)
		else:
			self.language: str = ""
			self.langsize: int = 0
	
	@property
	def graphics(self) -> bool:
		return self.graphicsnum > 2	#TODO figure this out
	
	def read(stream: io.BufferedIOBase) -> "LogoHeader":
		stream.read(3)	#LFG
		version: int = _readint(2, stream)
		graphicsnum: int = _readint32(stream)
		l = stream.read(1)[0]
		langoverride: bool = False
		langsize: int = 0
		language: str = ""
		if l == 0x4C:	#L
			langoverride = True
			stream.read(3)	#A 1
			langsize = _readint32(stream)
			language = stream.read(langsize).decode(_ENCODING)
			stream.read(1)	#T
		stream.read(3)	#X 1
		size: int = _readint32(stream)
		stream.read(2)	#;_
		header = LogoHeader(version, graphicsnum, langoverride, language)
		header.size = size
		return header
		
	def __bytes__(self) -> bytes:
		res: bytearray = bytearray(b"\x4C\x47\x46")	#LGF
		if self.version < 10:
			res.append(0x30)	#0
		res += str(self.version).encode(_ENCODING)
		res += _int32bytes(self.graphicsnum)
		if self.langoverride:
			res += b"\x4C\x41\x20\x31"	#LA 1
			res += _int32bytes(self.langsize)
			res += self.language.encode(_ENCODING)
		res += b"\x54\x58\x20\x31"	#TX 1
		res += _int32bytes(self.size)
		res += b"\x3B\x20"	#;_
		return bytes(res)

class LogoCommand:
	def __init__(self, _file: "LogoFile", raw: bytes):
		self._file: LogoFile = _file
		self._locales = self._file.settings._locales
		with io.BytesIO(raw) as stream:
			callees: List[str] = []
			currentcallee: bytearray = bytearray()
			while (current := stream.read(1)) != b"\x20":
				if current[0] == 0x27:
					callees.append(currentcallee.decode(_ENCODING))
					currentcallee = bytearray()
				else:
					currentcallee += current
			name = currentcallee.decode(_ENCODING)
			parameters = []
			currentvalue: bytearray = bytearray()
			escape: bool = False
			last2: int = -1
			last: int = -1
			lists = []
			strlevel: int = 0
			while (current := stream.read(1)) != b"":
				byte = current[0]
				if byte == 0x01:
					if len(lists) > 0 and len(lists[-1]) == 0:
						continue
					byte = 0x20
				if byte == 0x7C and not escape:	#|
					#escape = False
					if strlevel < 2:
						strlevel = 2
					else:
						if len(lists) > 0:
							lists[-1].append(_parsevalue(currentvalue, strlevel, True))
							if stream.read(2) != b"\x5C\x30":	#\0
								stream.seek(-1, os.SEEK_CUR)
						else:
							parameters.append(_parsevalue(currentvalue, strlevel, False))
						currentvalue = bytearray()
						strlevel = 0
				elif escape or strlevel == 2:
					currentvalue.append(byte)
					escape = False
				elif byte == 0x5C:	#\
					escape = True
				elif byte == 0x22:	#"
					if len(lists) > 0:
						currentvalue.append(byte)
					elif strlevel == 2:
						currentvalue.append(byte)
					elif strlevel == 0:
						strlevel = 1
					else:
						raise ValueError("Quotation mark error")
				elif byte == 0x5B:	#[
					lists.append([])
					if len(lists) > 1:
						lists[-2].append(lists[-1])
				elif byte == 0x5D:	#]
					if len(currentvalue) > 0:
						lists[-1].append(_parsevalue(currentvalue, strlevel, True))
					if len(lists) == 1:
						parameters.append(lists[0])
					del lists[-1]
					currentvalue = bytearray()
					strlevel = 0
				elif byte == 0x20:	#_
					if len(currentvalue) > 0:
						if len(lists) > 0:
							lists[-1].append(_parsevalue(currentvalue, strlevel, True))
						else:
							parameters.append(_parsevalue(currentvalue, strlevel, False))
						currentvalue = bytearray()
						strlevel = 0
				else:
					currentvalue.append(byte)
			if len(lists) > 0:
				if len(currentvalue) > 0:
					lists[-1].append(_parsevalue(currentvalue, strlevel, True))
				parameters.append(lists[0])
			elif len(currentvalue) > 0:
				parameters.append(_parsevalue(currentvalue, strlevel, False))
			self.callees = callees
			self.name = name.lower()
			self.parameters = parameters
			if self.name == self._locales.COMMAND_NEW:
				self._process_new()
			if self.name == self._locales.COMMAND_NEWCLASS:
				self._process_newclass()
			if self.name == self._locales.COMMAND_GLOBALVAR:
				self._process_globalvar()
			if self.name == self._locales.COMMAND_FIELDS:
				self._process_fields()
			if self.name == self._locales.COMMAND_WINDOWSTATE:
				self._process_window_state()
	
	def __str__(self) -> str:
		s: str = ""
		s += "'".join(self.callees)
		if len(self.callees) > 0:
			s += "'"
		s += self.name
		for v in self.parameters:
			s += " " + _tostr(v)
		return s
	
	def __bytes__(self) -> bytes:
		return str(self).encode(_ENCODING)
	
	def _process_new(self, window: bool = False):
		o: obj.Main = None
		classname: str = self.parameters[0].lower() if not window else self._locales.CLASS_MAINWINDOW
		location = self._file.window if not window else None
		if len(self.callees) > 0:
			location = self._file.name_to_object(self.callees[-1])
		o = self._file.name_to_object(classname)(location)
		definitions: dict[str, str] = {}
		events: dict[str, str] = {}
		ownvars: dict[str, object] = {}
		commonvars: dict[str, object] = {}
		listindex: int = 1 if not window else 0
		for i in range(0, len(self.parameters[listindex])-1, 2):
			key = self.parameters[listindex][i]
			value = self.parameters[listindex][i+1]
			if _process_setting(str(key), value, self._locales, definitions, events, ownvars, commonvars):
				continue
			o._change(key, value, True)
		o.definitions.update(definitions)
		o.events.update(events)
		o.ownvars.update(ownvars)
		o.commonvars.update(commonvars)
		if window:
			self._file.window = o
			for _obj in self._file.objects:
				if isinstance(_obj, obj.Main):
					if isinstance(_obj.__location__, obj.MainWindow):
						_obj.__location__ = self._file.window
				elif isinstance(_obj, type):
					if isinstance(_obj.classlocation, obj.MainWindow):
						_obj.classlocation = self._file.window
				else:
					raise TypeError(f"Unknown object type: {type(_obj)}")
		else:
			self._file.objects.append(o)
	
	def _process_newclass(self):
		base_class: str = self.parameters[0]
		classname: str = self.parameters[1]
		base_type: type = self._file.name_to_object(base_class)
		settings: dict[str, object] = deepcopy(base_type._DEFAULTS)
		definitions: dict[str, str] = {}
		events: dict[str, str] = {}
		ownvars: dict[str, object] = {}
		commonvars: dict[str, object] = {}
		for i in range(0, len(self.parameters[2])-1, 2):
			key = self.parameters[2][i]
			value = self.parameters[2][i+1]
			if _process_setting(str(key), value, self._locales, definitions, events, ownvars, commonvars):
				continue
			try:
				settingnum: int = int(key)
				if settingnum > 0 and settingnum <= len(obj.SETTINGS):
					settings[f"_{settingnum}"] = value
				else:
					ownvars[str(settingnum)] = value
			except ValueError:
				ownvars[key] = value
		def __init__(self, location):
			self._initialize(location)
		new_type: type = obj.LogoSettings("obj", **settings)(type(classname, (base_type,), {"__init__": __init__}))
		new_type.classlocation = self._file.window
		new_type.classdefinitions = deepcopy(new_type.classdefinitions)
		new_type.classdefinitions.update(definitions)
		new_type.classevents = deepcopy(new_type.classevents)
		new_type.classevents.update(events)
		new_type.classownvars = deepcopy(new_type.classownvars)
		new_type.classownvars.update(ownvars)
		new_type.classcommonvars = deepcopy(new_type.classcommonvars)
		new_type.classcommonvars.update(commonvars)
		self._file.objects.append(new_type)
		self._file.classes[classname] = new_type
	
	def _process_globalvar(self):
		self._file.globalvars[self.parameters[0]] = self.parameters[1]
	
	def _process_fields(self):
		table: str = self.parameters[0]
		if not table in self._file.fields:
			self._file.fields[table] = {}
		for i in range(0, len(self.parameters[1])-1, 2):
			key = self.parameters[1][i]
			value = self.parameters[1][i+1]
			self._file.fields[table][key] = value
	
	def _process_window_state(self):
		self._process_new(True)
		

class LogoFile:
	def __init__(self, header: LogoHeader, settings: LogoProjectSettings):
		self.header: LogoHeader = header
		self.settings: LogoProjectSettings = settings
		self.commands: List[LogoCommand] = []
		self.graphics: Optional[bytes] = b"" if self.header.graphics else None
		self.objects: List[obj.Main | type] = []
		self.window = obj.MainWindow(None)
		self.globalvars: dict[str, object] = {}
		self.fields: dict[str, dict[str, object]] = {}
		self.classes : dict[str, type] = {
			self.settings._locales.CLASS_MAIN: obj.Main,
			self.settings._locales.CLASS_MAINWINDOW: obj.MainWindow,
			self.settings._locales.CLASS_PAGE: obj.Page,
			self.settings._locales.CLASS_PANE: obj.Pane,
			self.settings._locales.CLASS_TOOLBAR: obj.ToolBar,
			self.settings._locales.CLASS_TURTLE: obj.Turtle,
			self.settings._locales.CLASS_TEXTBOX: obj.TextBox,
			self.settings._locales.CLASS_SLIDER: obj.Slider,
			self.settings._locales.CLASS_BUTTON: obj.Button,
			self.settings._locales.CLASS_TOOLBUTTON: obj.ToolButton,
			self.settings._locales.CLASS_WEB: obj.Web,
			self.settings._locales.CLASS_MEDIAPLAYER: obj.MediaPlayer,
			self.settings._locales.CLASS_NET: obj.Net,
			self.settings._locales.CLASS_JOYSTICK: obj.Joystick,
			self.settings._locales.CLASS_COMMPORT: obj.CommPort,
			self.settings._locales.CLASS_OLEOBJECT: obj.OleObject,
		}
	
	def write(self, path: str):
		self.update_header()
		with open(path, "wb") as f:
			f.write(bytes(self.header))
			f.write(bytes(self.settings))
			for cmd in self.commands:
				f.write(b"\x0D\x0A\x0D\x0A")	#\r\n\r\n
				f.write(bytes(cmd))
			f.write(b"\x0D\x0A")	#\r\n
			if self.header.graphics:
				f.write(self.graphics)
	
	def update_header(self):
		self.header.size = 4	#;_ [...] \r\n
		self.header.size += len(bytes(self.settings))
		for cmd in self.commands:
			self.header.size += len(bytes(cmd)) + 4	#\r\n\r\n
	
	def read(path: str) -> "LogoFile":
		with open(path, "rb") as f:
			header: LogoHeader = LogoHeader.read(f)
			commandsraw: bytes = f.read(header.size - 2)
			graphicsraw: bytes = f.read()
			with io.BytesIO(commandsraw) as commandsstream:
				settings: LogoProjectSettings = LogoProjectSettings.read(commandsstream)
				lfile: LogoFile = LogoFile(header, settings)
				commands: List[LogoCommand] = []
				while (cmd := _get_command_bytes(commandsstream)) != None:
					if cmd:
						commands.append(LogoCommand(lfile, cmd))
		lfile.commands = commands
		if header.graphics:
			lfile.graphics = graphicsraw
		return lfile
	
	def cmd_from_str(self, cmd: str) -> LogoCommand:
		return LogoCommand(self, cmd.encode(_ENCODING))
	
	def index_to_object(self, index: int):
		if index < 1 or index > len(self.objects):
			raise IndexError("Index out of range")
		return self.objects[index-1]
	
	def name_to_object(self, name: str):
		if not name:
			raise ValueError("Empty name")
		if name.startswith("#"):
			return self.index_to_object(int(name[1:]))
		if name in self.classes:
			return self.classes[name]
		for o in self.objects:
			if o.__name__ == name:
				return o
		raise ValueError("Object not found: " + name)

def _printobj(o: obj.Main | type):
	print(f"\tTeljes: {_tolocation(o)}")
	if isinstance(o, obj.Main):
		print("\tBeállítások")
		for key in o._settings:
			setting = o._settings[key]
			print(f"\t\t{setting.name} ({key}): {getattr(o, setting.name)}")
		print("\tEljárások")
		for key in o.definitions:
			print(f"\t\t{key}")
			print("\t\t\t" + o.definitions[key].replace("\n", "\n\t\t\t"))
		print("\tEsemények")
		for key in o.events:
			print(f"\t\t{key}: {o.events[key]}")
		print(f"\tSaját változók")
		for key in o.ownvars:
			print(f"\t\t{key}: {o.ownvars[key]}")
		print(f"\tKözös változók")
		for key in o.commonvars:
			print(f"\t\t{key}: {o.commonvars[key]}")
	elif isinstance(o, type):
		print("\tEljárások")
		for key in o.classdefinitions:
			print(f"\t\t{key}")
			print("\t\t\t" + o.classdefinitions[key].replace("\n", "\n\t\t\t"))
		print("\tEsemények")
		for key in o.classevents:
			print(f"\t\t{key}: {o.classevents[key]}")
		print(f"\tSaját változók")
		for key in o.classownvars:
			print(f"\t\t{key}: {o.classownvars[key]}")
		print(f"\tKözös változók")
		for key in o.classcommonvars:
			print(f"\t\t{key}: {o.classcommonvars[key]}")
	else:
		raise TypeError(f"Unknown type: {type(o)}")

if __name__ == "__main__":
	TESTFILE = "demo_recreated"
	f = LogoFile.read(f"testfiles/{TESTFILE}.IMP")
	print("====Parancsok====")
	for cmd in f.commands:
		print(str(cmd))
	print("====Objektumok====")
	print("Főablak")
	_printobj(f.window)
	for i in range(len(f.objects)):
		o = f.objects[i]
		print(f"#{i+1}: {o.__name__} [{type(o).__name__}]")
		_printobj(o)
	f.write(f"testfiles_recreated/{TESTFILE}_recreated.IMP")
