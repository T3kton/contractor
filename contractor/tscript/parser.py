from datetime import timedelta

from contractor.tscript.parsimonious import Grammar, IncompleteParseError

grammar = Grammar( """
script              = lines
lines               = line*
line                = ( expression / ws_s ) comment? nl_p
expression          = ws_s ( jump_point / function / ifelse / whiledo / block / assignment / infix / boolean / not_ / none / other / array_item / array / variable / time / number_float / number_int / text ) ws_s
value_expression    = ws_s ( function / assignment / infix / boolean / not_ / none / array_item / array / variable / time / number_float / number_int / text ) ws_s
constant_expression = ws_s ( boolean / none / time / number_float / number_int / text ) ws_s
comment             = "#" ~"[^\\r\\n]*"
jump_point          = ":" label
paramater_map       = ( ( ws_s label ws_s "=" value_expression "," )* ws_s label ws_s "=" value_expression )? ws_s
const_paramater_map = ( ( ws_s label ws_s "=" constant_expression "," )* ws_s label ws_s "=" constant_expression )? ws_s
block               = "begin(" const_paramater_map ")" lines "end"

whiledo             = "while" value_expression ws_s "do" ws_s nl_s expression
other               = ( "continue" / "break" / "pass" )

ifelse              = "if" value_expression ws_s "then" ws_s nl_s expression ( nl_s ws_s "elif" ws_s value_expression ws_s "then" ws_s nl_s expression )* ( nl_s ws_s "else" ws_s nl_s expression )?

not_                = ~"[Nn]ot" value_expression

time                = ~"([0-9]{1,2}:){1,3}[0-9]{1,2}"
number_float        = ~"[-+]?[0-9]+\.[0-9]+"
number_int          = ~"[-+]?[0-9]+"
text                = ( "'" ~"[^']*" "'" ) / ( '"' ~'[^"]*' '"' )
boolean             = ~"[Tt]rue" / ~"[Ff]alse"
none                = ~"[Nn]one"

array               = "[" ( ( value_expression "," )* value_expression )? ws_s "]"

function            = !"begin(" ( label "." )* label "(" paramater_map ")"
variable            = !( "begin" / "end" / "while" / "do" / other ) ( label "." )* label !"("
array_item          = variable "[" value_expression "]"

infix               = "(" value_expression ( "^" / "*" / "/" / "%" / "+" / "-" / "&" / "|" / "&&"/ "||" / "==" / "!=" / ">" / "<" / "<=" / "<>" ) value_expression ")"

assignment          = ( array_item / variable ) ws_s "=" value_expression

label               = ~"[a-zA-Z][a-zA-Z0-9_]+"
ws_o                = ~"[ \t]"
ws_s                = ~"[ \t]*"
ws_p                = ~"[ \t]+"
nl_o                = ~"[\\r\\n]"
nl_s                = ~"[\\r\\n]*"
nl_p                = ~"[\\r\\n]+"

""" )

class types():
  SCOPE = 'S'
  JUMP_POINT = 'J'
  CONSTANT = 'C'
  INFIX = 'X'
  WHILE = 'W'
  IFELSE = 'I'
  VARIABLE = 'V'
  ARRAY_ITEM = 'R'
  ARRAY = 'Y'
  FUNCTION = 'F'
  NOT = 'N'
  ASSIGNMENT = 'A'
  OTHER = 'O'


class ParseError( Exception ):
  def __init__( self, line, column, msg ):
    self.line = line
    self.column = column
    self.msg = msg

  def __str__( self ):
    return 'ParseError, line: {0}, column: {1}, "{2}"'.format( self.line, self.column, self.msg )

def lint( script ):
  parser = Parser()
  script += '\n' # just incase the end of the script lacks a \n otherwise the *line* will not match
  try:
    ast = grammar.parse( script )
  except IncompleteParseError as e:
    return 'Incomplete Parsing on line: {0} column: {1}'.format( e.line(), e.column() )
    
  try:
    parser._eval( ast )
  except Exception as e:
    return 'Exception Parsing "{0}"'.format( e )

  return None


def parse( script ):
  #print( '---------------------' )
  #print( script )
  #print( '=====================' )
  parser = Parser()
  script += '\n' # just incase the end of the script lacks a \n otherwise the *line* will not match
  try:
    ast = grammar.parse( script )
  except IncompleteParseError as e:
    raise ParseError( e.line(), e.column(), 'Incomplete Parse' )

  return ( types.SCOPE, { '_children': parser._eval( ast ) } )


class IsEmpty( Exception ):
  pass


class Parser( object ):
  def __init__( self, *args, **kwargs ):
    super().__init__( *args, **kwargs )
    
  def _eval( self, node ):
    #print( '~~{0}~~'.format( node.expr_name ) )
    if node.expr_name[ 0:3 ] in ( 'ws_', 'nl_' ):  # ignore wite space
      raise IsEmpty()
    
    try:  
      handler = getattr( self, node.expr_name )
    except AttributeError:
      handler = self.anonymous

    return handler( node )
    
  def anonymous( self, node ):
    if len( node.children ) < 1:
      raise IsEmpty()
      
    return self._eval( node.children[0] )
    
  def lines( self, node ):
    if not node.children:
      return []
    
    result = []
    for child in node.children:
      try:
        result.append( self._eval( child ) )
      except IsEmpty:
        pass
    
    return result

  def line( self, node ):
    return self._eval( node.children[0] )

  def expression( self, node ):
    #print( 'Expression "{0}"'.format( node.children[1] ) )
    return self._eval( node.children[1] )

  def value_expression( self, node ):
    return self._eval( node.children[1] )
  
  def constant_expression( self, node ):
    return self._eval( node.children[1] )
  
  def block( self, node ):
    options = self._eval( node.children[1] )
    options[ '_children' ] = self._eval( node.children[3] )
    
    return ( types.SCOPE, options )

  def paramater_map( self, node ):
    children = node.children[0].children
    if len( children ) == 0:
      return {}

    children = children[0].children
    groups = [ children[1:] ]
    for item in children[0]:
      groups.append( item.children )
      
    result = {}
    for item in groups:
      try:
        result[ item[1].text ] = self._eval( item[4] )
      except IsEmpty:
        raise Exception( 'Paramater values are not allowed to be IsEmpty' )

    return result

  def const_paramater_map( self, node ):
    result = self.paramater_map( node )
    for key in result.keys():
      if result[ key ][0] != types.CONSTANT:
        raise Exception( 'Expected Constant paramater, got type "{0}"'.format( result[ key ][0] ) )
        
      result[ key ] = result[ key ][1]
      
    return result

  def jump_point( self, node ):
    return ( types.JUMP_POINT, node.children[1].text )

  def time( self, node ): # days:hours:mins:seconds
    parts = [ int( i ) for i in node.text.split( ':' ) ]
    
    if len( parts ) == 4:
      return ( types.CONSTANT, timedelta( days=parts[0], hours=parts[1], minutes=parts[2], seconds=parts[3] ) )
    elif len( parts ) == 3:
      return ( types.CONSTANT, timedelta( hours=parts[0], minutes=parts[1], seconds=parts[2] ) )
    else:
      return ( types.CONSTANT, timedelta( minutes=parts[0], seconds=parts[1] ) )

  def number_float( self, node ):
    return ( types.CONSTANT, float( node.text ) )

  def number_int( self, node ):
    return ( types.CONSTANT, int( node.text ) )

  def boolean( self, node ):
    return ( types.CONSTANT, True if node.text.lower() == 'true' else False )

  def text( self, node ):
    return ( types.CONSTANT, node.children[0].children[1].text )

  def none( self, node ):
    return ( types.CONSTANT, None )

  def array( self, node ):
    children = node.children[1].children
    if len( children ) == 0:
      return ( types.ARRAY, [] )

    children = children[0].children
    values = []
    for item in children[0]:
      values.append( self._eval( item ) )
      
    values.append( self._eval( children[1] ) )
    
    return ( types.ARRAY, values )

  def variable( self, node ):
    name = node.children[1].text + node.children[2].text
    
    return ( types.VARIABLE, name )

  def array_item( self, node ):
    variable = self._eval( node.children[0] )
    if variable[0] != types.VARIABLE:
      raise Exception( 'Can only index variables' )
      
    index = self._eval( node.children[2] )
    
    return ( types.ARRAY_ITEM, { 'name': variable[1], 'index': index } )

  def infix( self, node ):
    return ( types.INFIX, { 'operator': node.children[2].text, 'left': self._eval( node.children[1] ), 'right': self._eval( node.children[3] ) } )

  def other( self, node ):
    return ( types.OTHER, node.children[0].text )
 
  def not_( self, node ):
    return ( types.NOT, self._eval( node.children[1] ) )
    
  def whiledo( self, node ):
    return ( types.WHILE, { 'condition': self._eval( node.children[1] ), 'expression': self._eval( node.children[6] ) } )

  def ifelse( self, node ):
    branches = []
    
    branches.append( { 'condition': self._eval( node.children[1] ), 'expression': self._eval( node.children[6] ) } )
    
    for item in node.children[7].children:
      branches.append( { 'condition': self._eval( item.children[4] ), 'expression': self._eval( item.children[9] ) } )
  
    if len( node.children[8].children ) > 0:
      branches.append( { 'condition': None, 'expression': self._eval( node.children[8].children[0].children[5] ) } )
    
    return ( types.IFELSE, branches )
    
  def function( self, node ):
    name = node.children[1].text + node.children[2].text
    
    params = self._eval( node.children[4] )

    return ( types.FUNCTION, { 'name': name, 'paramaters': params } )
    
  def assignment( self, node ):
    target = self._eval( node.children[0] )
    
    return ( types.ASSIGNMENT, { 'target': target, 'value': self._eval( node.children[3] ) } )
  
  
  
  

