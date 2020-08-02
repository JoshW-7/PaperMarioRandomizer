
============================
  RULES
----------------------------

entries:
- each line contains one entry associating a name unique RAM address/ROM offset within the scope of the library
- lines may 'continue' onto the next line if they end with "..."
- entries can be functions, scripts, or data structures

fields and tokens:
- fields within each entry are separated by :
- descriptions for each field are enclosed within ""
- options for a field are enclosed within {}, 
- parameter lists within a field are separated by ,
- the remaining elements are tokens, separated by whitespace

limitations:
- tokens may only contain alphanumeric and _*?# characters
- descriptions and options may occur at any position within a field
- a field may have multiple options, but only one description
- descriptions may contain any characters, including " and \ through escape sequence: \" and \\
- options may contain any character EXCEPT {}
- EOL comments are allowed, even on continued lines, and will not be read by the parser

============================
  FORMAT
----------------------------

The general format for an entry is:

TYPE : LOCATION : NAME : ...

NAME must contain only letters, digits, and underscores
LOCATION may be either an address or an address/offset pair separated by ,
TYPE may refer to any of the following: asm, api, scr, dat
additional fields depend on the type.

============================
ENTRY TYPES
----------------------------

(1) asm = function
    asm : LOCATION : NAME : RETURNS : PARAMS
 + only one return value allowed
 + parameters are always stored in registers

(2) api     function available to scripts
    api : LOCATION : NAME : RETURNS : PARAMS
 + always called with A0 = caller script_context*, A1 = bIsInitialCall
 + expected to return a scritpt result emum value
 + return values are stored in game variables (Var[0], Var[2], etc)
 + multiple return values allowed

(3) scr     script
    scr : LOCATION : NAME : RETURNS : PARAMS
 + parameters may be either int or float depending on whether they are to be dereferenced with get_variable or get_float_variable.
 + return values are stored in game variables (Var[0], Var[2], etc)

(4) dat    data
    scr : LOCATION : NAME : TYPE

============================
  PARAMETERS
----------------------------

Both RETURNS and PARAMS are comma-separated lists of 'parameters' having one of the following formats:
(1) type
(2) type name
(3) storage type name
The difference between them is simply the number of whitespace-separated tokens.

Empty lists are indicated by "void"
Unknown lists are indicated by "???"
asm functions may have "varargs" for the PARAMS field

Types come in five categories:
(a) 'c' types, like actor, entity, etc. these are structs used at runtime. you will often see these are passed around as pointers in the library asm entries.
(b) static types, like $Script or $Actor. these are the structs printed by Star Rod for script files. they are found in the data files for maps/formations/etc and typically loaded to a corresponding 'c' type at runtime. these types are always prefixed with $.
(c) enum types, like #actorID or #itemID. corresponding to a Star Rod enum from the database/types folder. flags fields may also be represented this way.
(d) var/fvar are special types indicating a valid variable reference like FE363C80 or F8405B80.
(e) typedefs, like stringID or vec3f*, corresponding to values in database/structs/typedefs.txt

============================
  STORAGE
----------------------------

register        A0, S3, F12, SP, etc.
stack           SP[10], SP[0], SP[44], etc.
var             Var[0], Var[A], etc. (also valid: AreaByte[4], GameFlag[1], etc.)

asm params      registers, stack
asm returns     registers, stack
api params      none
api returns     var only
scr params      var only
scr returns     var only

============================
  OPTIONS
----------------------------

library:
version=S   version string
scope=S     common|world|battle

dumping system (only valid on args with static type -- $T):
api     param   name=X              name suffix
api     param   len=X               array length (X can be #N to indicate 'get value from Nth arg')

mod developer notes:
asm     param   out                 returns value
api     param   outType=S           out type in variable (can be any valid type, including an enum with # or a static pointer with $)
api     param   raw                 getVariable not used to read this param (missing alot of these, added late in the documentation process)
api     param   ignore=X            indicates the get/set involving this field will be skipped if its value equals the magic number X
api     param   print               
*       entry   warning=unused      never used in vanilla, still functions properly
*       entry   warning=invalid     improper signature that nevertheless functions
*       entry   warning=bugged      function is broken in some way
*       entry   warning=internal    used by the engine for some specific task, not intended for general use. probably should be hidden in suggestions.
