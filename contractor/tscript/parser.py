from datetime import timedelta

from parsimonious import Grammar, ParseError, IncompleteParseError


tscript_grammar = r"""
script              = lines
lines               = line*
line                = ( expression / ws_s ) comment? nl_p
expression          = ws_s ( jump_point / goto / function / ifelse / whiledo / block / assignment / infix / boolean / not_ / none / exists / other / array_map_item / array / map / variable / time / number_float / number_int / text ) ws_s
value_expression    = ws_s ( function / assignment / infix / boolean / not_ / none / exists / array_map_item / array / map / variable / time / number_float / number_int / text ) ws_s
constant_expression = ws_s ( boolean / none / time / number_float / number_int / text ) ws_s
comment             = "#" ~"[^\\r\\n]*"
jump_point          = ":" label
goto                = "goto " label
paramater_map       = ( ( ws_s label ws_s "=" value_expression "," )* ws_s label ws_s "=" value_expression )? ws_s
const_paramater_map = ( ( ws_s label ws_s "=" constant_expression "," )* ws_s label ws_s "=" constant_expression )? ws_s
block               = "begin(" const_paramater_map ")" lines ws_s "end"

whiledo             = "while" value_expression "do" em_p expression
other               = ( "continue" / "break" / "pass" )

ifelse              = "if" value_expression "then" em_p expression ( em_s "elif" value_expression "then" em_p expression )* ( em_s "else" em_p expression )?

not_                = ~"[Nn]ot" value_expression

time                = ~"([0-9]{1,2}:){1,3}[0-9]{1,2}"
number_float        = ~"[-+]?[0-9]+\\.[0-9]+"
number_int          = ~"[-+]?[0-9]+"
text                = ( "'" ~"[^']*" "'" ) / ( '"' ~'[^"]*' '"' )
boolean             = ~"[Tt]rue" / ~"[Ff]alse"
none                = ~"[Nn]one"
exists              = "exists(" ws_s ( array_map_item / variable ) ws_s ")"

array               = "[" ( ( value_expression "," )* value_expression )? ws_s "]"
map                 = "{" paramater_map "}"

reserved            = ( "begin" / "end" / "while" / "do" / "goto" / "exists" / other ) !~"[a-zA-Z0-9_]"
variable            = !reserved ( label "." )? label !"("

function            = !reserved ( label "." )? label "(" paramater_map ")"
array_map_item      = variable "[" value_expression "]"

infix               = "(" value_expression ( "." / "^" / "*" / "/" / "%" / "+" / "-" / "&" / "|" / "and"/ "or" / "==" / "!=" / "<=" / ">=" / ">" / "<" ) value_expression ")"

assignment          = ( array_map_item / variable ) ws_s "=" value_expression

label               = ~"[a-zA-Z][a-zA-Z0-9_]+"
ws_o                = ~"[ \\x09]"
ws_s                = ~"[ \\x09]*"
ws_p                = ~"[ \\x09]+"
nl_o                = ~"[\\x0d\\x0a]"
nl_s                = ~"[\\x0d\\x0a]*"
nl_p                = ~"[\\x0d\\x0a]+"
em_o                = ~"[\\x0d\\x0a \\x09]"
em_s                = ~"[\\x0d\\x0a \\x09]*"
em_p                = ~"[\\x0d\\x0a \\x09]+"
"""


class Types():
  LINE = 'L'
  SCOPE = 'S'
  JUMP_POINT = 'J'
  GOTO = 'G'
  CONSTANT = 'C'
  INFIX = 'X'
  WHILE = 'W'
  IFELSE = 'I'
  VARIABLE = 'V'
  ARRAY_MAP_ITEM = 'R'
  ARRAY = 'Y'
  MAP = 'M'
  FUNCTION = 'F'
  ASSIGNMENT = 'A'
  EXISTS = 'E'
  OTHER = 'O'


class ParserError( Exception ):
  def __init__( self, line, column, msg ):
    self.line = line
    self.column = column
    self.msg = msg

  def __str__( self ):
    return 'ParseError, line: {0}, column: {1}, "{2}"'.format( self.line, self.column, self.msg )


def lint( script ):
  parser = Parser()
  return parser.lint( script )


def parse( script ):
  parser = Parser()
  return parser.parse( script )


class IsEmpty( Exception ):
  pass


class Parser( object ):
  def __init__( self ):
    super().__init__()
    self.line_endings = []
    self.grammar = Grammar( tscript_grammar )

  def lint( self, script ):
    script += '\n'  # just incase the end of the script lacks a \n otherwise the *line* will not match
    self.line_endings = [ i for i, c in enumerate( script ) if c == '\n' ]
    try:
      root_node = self.grammar.parse( script )
    except IncompleteParseError as e:
      return 'Incomplete Parsing on line: {0} column: {1}'.format( e.line(), e.column() )
    except ParseError as e:
      return 'Error Parsing on line: {0} column: {1}'.format( e.line(), e.column() )

    try:
      ast = self._eval( root_node )
    except Exception as e:
      return 'Exception Parsing "{0}"'.format( e )

    try:
      self._check( ast )
    except ParserError as e:
      return 'Invalid Script "{0}", line: {1} column: {2}'.format( e.msg, e.line, e.column )

    return None

  def parse( self, script ):
    script += '\n'  # just incase the end of the script lacks a \n otherwise the *line* will not match
    self.line_endings = [ i for i, c in enumerate( script ) if c == '\n' ]
    try:
      root_node = self.grammar.parse( script )
    except IncompleteParseError as e:
      raise ParserError( e.line(), e.column(), 'Incomplete Parse' )
    except ParseError as e:
      raise ParserError( e.line(), e.column(), 'Error Parsing' )

    ast = self._eval( root_node )
    self._check( ast )

    return ( Types.SCOPE, { '_children': ast, 'description': 'Overall Script' } )

  def _eval( self, node ):
    if node.expr_name[ 0:3 ] in ( 'ws_', 'nl_', 'em_' ):  # ignore wite space
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
    for i in range( 0, len( self.line_endings ) ):
      if self.line_endings[ i ] > node.start:
        break

    return ( Types.LINE, self._eval( node.children[0] ), i + 1 )

  def expression( self, node ):
    return self._eval( node.children[1] )

  def value_expression( self, node ):
    return self._eval( node.children[1] )

  def constant_expression( self, node ):
    return self._eval( node.children[1] )

  def block( self, node ):
    options = self._eval( node.children[1] )
    for name in options.keys():
      if name not in ( 'description', 'expected_time', 'max_time' ):
        raise Exception( 'Scope option "{0}" not valid'.format( name ) )  # or ParseError ?  probably need to check the other "raises Eception" too

    options[ '_children' ] = self._eval( node.children[3] )

    return ( Types.SCOPE, options )

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
      if result[ key ][0] != Types.CONSTANT:
        raise Exception( 'Expected Constant paramater, got type "{0}"'.format( result[ key ][0] ) )

      result[ key ] = result[ key ][1]

    return result

  def jump_point( self, node ):
    return ( Types.JUMP_POINT, node.children[1].text )

  def goto( self, node ):
    return ( Types.GOTO, node.children[1].text )

  def time( self, node ):  # days:hours:mins:seconds
    parts = [ int( i ) for i in node.text.split( ':' ) ]

    if len( parts ) == 4:
      return ( Types.CONSTANT, timedelta( days=parts[0], hours=parts[1], minutes=parts[2], seconds=parts[3] ) )
    elif len( parts ) == 3:
      return ( Types.CONSTANT, timedelta( hours=parts[0], minutes=parts[1], seconds=parts[2] ) )
    else:
      return ( Types.CONSTANT, timedelta( minutes=parts[0], seconds=parts[1] ) )

  def number_float( self, node ):
    return ( Types.CONSTANT, float( node.text ) )

  def number_int( self, node ):
    return ( Types.CONSTANT, int( node.text ) )

  def boolean( self, node ):
    return ( Types.CONSTANT, True if node.text.lower() == 'true' else False )

  def text( self, node ):
    return ( Types.CONSTANT, node.children[0].children[1].text )

  def none( self, node ):
    return ( Types.CONSTANT, None )

  def exists( self, node ):
    return ( Types.EXISTS, self._eval( node.children[2] ) )

  def array( self, node ):
    children = node.children[1].children
    if len( children ) == 0:
      return ( Types.ARRAY, [] )

    children = children[0].children
    values = []
    for item in children[0]:
      values.append( self._eval( item ) )

    values.append( self._eval( children[1] ) )

    return ( Types.ARRAY, values )

  def map( self, node ):
    values = self._eval( node.children[1] )

    return ( Types.MAP, values )

  def variable( self, node ):
    if len( node.children[1].children ) > 0:
      module = node.children[1].children[0].children[0].text
    else:
      module = None

    return ( Types.VARIABLE, { 'module': module, 'name': node.children[2].text } )

  def array_map_item( self, node ):
    variable = self._eval( node.children[0] )
    if variable[0] != Types.VARIABLE:
      raise Exception( 'Can only index variables' )

    index = self._eval( node.children[2] )
    return ( Types.ARRAY_MAP_ITEM, { 'module': variable[1][ 'module' ], 'name': variable[1][ 'name' ], 'index': index } )

  def infix( self, node ):
    return ( Types.INFIX, { 'operator': node.children[2].text, 'left': self._eval( node.children[1] ), 'right': self._eval( node.children[3] ) } )

  def not_( self, node ):  # we are going to abuse the INFIX functino for this one
    return ( Types.INFIX, { 'operator': 'not', 'left': self._eval( node.children[1] ), 'right': ( Types.CONSTANT, None ) } )

  def other( self, node ):
    return ( Types.OTHER, node.children[0].text )

  def whiledo( self, node ):
    return ( Types.WHILE, { 'condition': self._eval( node.children[1] ), 'expression': self._eval( node.children[4] ) } )

  def ifelse( self, node ):
    branches = []
    branches.append( { 'condition': self._eval( node.children[1] ), 'expression': self._eval( node.children[4] ) } )

    for item in node.children[5].children:
      branches.append( { 'condition': self._eval( item.children[2] ), 'expression': self._eval( item.children[5] ) } )

    if len( node.children[6].children ) > 0:
      branches.append( { 'condition': None, 'expression': self._eval( node.children[6].children[0].children[3] ) } )

    return ( Types.IFELSE, branches )

  def function( self, node ):
    params = self._eval( node.children[4] )

    if len( node.children[1].children ) > 0:
      module = node.children[1].children[0].children[0].text
    else:
      module = None

    return ( Types.FUNCTION, { 'module': module, 'name': node.children[2].text, 'paramaters': params } )

  def assignment( self, node ):
    target = self._eval( node.children[0] )

    return ( Types.ASSIGNMENT, { 'target': target, 'value': self._eval( node.children[3] ) } )

  def _check( self, ast ):  # TODO: also check infix operators that they are operating against the right type of paramaters, as far as the constansts are anyway
    node_stack = [ ( ast, 0 ) ]

    while node_stack:
      node_list, stack_depth = node_stack.pop( 0 )
      for i in range( 0, len( node_list ) ):
        line_no = node_list[i][2]
        node = node_list[i][1]
        if node[0] == Types.JUMP_POINT and stack_depth > 0:
          raise ParserError( line_no, 0, 'Jump points can not be inside begin/end blocks, jump point name: "{0}"'.format( node[1] ) )

        elif node[0] == Types.SCOPE:
          node_stack.append( ( node[1][ '_children' ], stack_depth + 1 ) )
