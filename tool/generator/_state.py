from constants_gen import *
from enums_gen import *
from flags_gen import *
from structs_gen import *
from objects_gen import *
from functions_gen import *
from callbacks_gen import *
from types_gen import *

spec: dict[str, dict]

CONSTANTS: dict[str, ConstantDecl] = {}
ENUMS: dict[str, EnumDecl] = {}
FLAGS: dict[str, FlagDecl] = {}
STRUCTS: dict[str, StructDecl] = {}
OBJECTS: dict[str, ObjectDecl] = {}
GLOBAL_FUNCTIONS: dict[str, FunctionDecl] = {}
CALLBACKS: dict[str, CallbackDecl] = {}


def get_constant(name: str) -> ConstantDecl: return CONSTANTS[name]
def get_enum(name: str) -> EnumDecl: return ENUMS[name]
def get_flag(name: str) -> FlagDecl: return FLAGS[name]
def get_struct(name: str) -> StructDecl: return STRUCTS[name]
def get_object(name: str) -> ObjectDecl: return OBJECTS[name]
def get_global_function(name: str) -> FunctionDecl: return GLOBAL_FUNCTIONS[name]
def get_callback(name: str) -> CallbackDecl: return CALLBACKS[name]
