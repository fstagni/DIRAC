# $HeadURL$

###############################################################################
#                            DEncode.py                                       #
###############################################################################
"""
Encoding and decoding for dirac, Ids:
 i -> int
 I -> long
 f -> float
 b -> bool
 s -> string
 z -> datetime
 n -> none
 l -> list
 t -> tuple
 d -> dictionary
"""

__RCSID__ = "$Id$"

import json
import types
import datetime

#data types used for date and time encoding
_dateTimeObject = datetime.datetime.utcnow()
_dateTimeType = type( _dateTimeObject )
_dateType = type( _dateTimeObject.date() )
_timeType = type( _dateTimeObject.time() )

################################################################################
#                   Old code for DEncode (un)marshalling                       #
################################################################################
g_dEncodeFunctions = {}
g_dDecodeFunctions = {}

#Encoding and decoding ints
def encodeInt( iValue, eList ):
  eList.extend( ( "i", str( iValue ), "e" ) )

def decodeInt( data, i ):
  i += 1
  end = data.index( 'e', i )
  value = int( data[i:end] )
  return ( value, end + 1 )

g_dEncodeFunctions[ types.IntType ] = encodeInt
g_dDecodeFunctions[ "i" ] = decodeInt

#Encoding and decoding longs
def encodeLong( iValue, eList ):
  # corrected by KGG   eList.extend( ( "l", str( iValue ), "e" ) )
  eList.extend( ( "I", str( iValue ), "e" ) )

def decodeLong( data, i ):
  i += 1
  end = data.index( 'e', i )
  value = long( data[i:end] )
  return ( value, end + 1 )

g_dEncodeFunctions[ types.LongType ] = encodeLong
g_dDecodeFunctions[ "I" ] = decodeLong

#Encoding and decoding floats
def encodeFloat( iValue, eList ):
  eList.extend( ( "f", str( iValue ), "e" ) )

def decodeFloat( data, i ):
  i += 1
  end = data.index( 'e', i )
  if end + 1 < len( data ) and data[end + 1] in ( '+', '-' ):
    eI = end
    end = data.index( 'e', end + 1 )
    value = float( data[i:eI] ) * 10 ** int( data[eI + 1:end] )
  else:
    value = float( data[i:end] )
  return ( value, end + 1 )

g_dEncodeFunctions[ types.FloatType ] = encodeFloat
g_dDecodeFunctions[ "f" ] = decodeFloat

#Encoding and decoding booleand
def encodeBool( bValue, eList ):
  if bValue:
    eList.append( "b1" )
  else:
    eList.append( "b0" )

def decodeBool( data, i ):
  if data[ i + 1 ] == "0":
    return ( False, i + 2 )
  else:
    return ( True, i + 2 )

g_dEncodeFunctions[ types.BooleanType ] = encodeBool
g_dDecodeFunctions[ "b" ] = decodeBool

#Encoding and decoding strings
def encodeString( sValue, eList ):
  eList.extend( ( 's', str( len( sValue ) ), ':', sValue ) )

def decodeString( data, i ):
  i += 1
  colon = data.index( ":", i )
  value = int( data[ i : colon ] )
  colon += 1
  end = colon + value
  return ( data[ colon : end] , end )

g_dEncodeFunctions[ types.StringType ] = encodeString
g_dDecodeFunctions[ "s" ] = decodeString

#Encoding and decoding unicode strings
def encodeUnicode( sValue, eList ):
  valueStr = sValue.encode( 'utf-8' )
  eList.extend( ( 'u', str( len( valueStr ) ), ':', valueStr ) )

def decodeUnicode( data, i ):
  i += 1
  colon = data.index( ":", i )
  value = int( data[ i : colon ] )
  colon += 1
  end = colon + value
  return ( unicode( data[ colon : end], 'utf-8' ) , end )

g_dEncodeFunctions[ types.UnicodeType ] = encodeUnicode
g_dDecodeFunctions[ "u" ] = decodeUnicode

#Encoding and decoding datetime
def encodeDateTime( oValue, eList ):
  if type( oValue ) == _dateTimeType:
    tDateTime = ( oValue.year, oValue.month, oValue.day, \
                      oValue.hour, oValue.minute, oValue.second, \
                      oValue.microsecond, oValue.tzinfo )
    eList.append( "za" )
    # corrected by KGG encode( tDateTime, eList )
    g_dEncodeFunctions[ type( tDateTime ) ]( tDateTime, eList )
  elif type( oValue ) == _dateType:
    tData = ( oValue.year, oValue.month, oValue. day )
    eList.append( "zd" )
    # corrected by KGG encode( tData, eList )
    g_dEncodeFunctions[ type( tData ) ]( tData, eList )
  elif type( oValue ) == _timeType:
    tTime = ( oValue.hour, oValue.minute, oValue.second, oValue.microsecond, oValue.tzinfo )
    eList.append( "zt" )
    # corrected by KGG encode( tTime, eList )
    g_dEncodeFunctions[ type( tTime ) ]( tTime, eList )
  else:
    raise Exception( "Unexpected type %s while encoding a datetime object" % str( type( oValue ) ) )

def decodeDateTime( data, i ):
  i += 1
  dataType = data[i]
  # corrected by KGG tupleObject, i = decode( data, i + 1 )
  tupleObject, i = g_dDecodeFunctions[ data[ i + 1 ] ]( data, i + 1 )
  if dataType == 'a':
    dtObject = datetime.datetime( *tupleObject )
  elif dataType == 'd':
    dtObject = datetime.date( *tupleObject )
  elif dataType == 't':
    dtObject = datetime.time( *tupleObject )
  else:
    raise Exception( "Unexpected type %s while decoding a datetime object" % dataType )
  return ( dtObject, i )

g_dEncodeFunctions[ _dateTimeType ] = encodeDateTime
g_dEncodeFunctions[ _dateType ] = encodeDateTime
g_dEncodeFunctions[ _timeType ] = encodeDateTime
g_dDecodeFunctions[ 'z' ] = decodeDateTime

#Encoding and decoding None
def encodeNone( oValue, eList ):
  eList.append( "n" )

def decodeNone( data, i ):
  return ( None, i + 1 )

g_dEncodeFunctions[ types.NoneType ] = encodeNone
g_dDecodeFunctions[ 'n' ] = decodeNone

#Encode and decode a list
def encodeList( lValue, eList ):
  eList.append( "l" )
  for uObject in lValue:
    g_dEncodeFunctions[ type( uObject ) ]( uObject, eList )
  eList.append( "e" )

def decodeList( data, i ):
  oL = []
  i += 1
  while data[ i ] != "e":
    ob, i = g_dDecodeFunctions[ data[ i ] ]( data, i )
    oL.append( ob )
  return( oL, i + 1 )

g_dEncodeFunctions[ types.ListType ] = encodeList
g_dDecodeFunctions[ "l" ] = decodeList

#Encode and decode a tuple
def encodeTuple( lValue, eList ):
  eList.append( "t" )
  for uObject in lValue:
    g_dEncodeFunctions[ type( uObject ) ]( uObject, eList )
  eList.append( "e" )

def decodeTuple( data, i ):
  oL, i = decodeList( data, i )
  return ( tuple( oL ), i )

g_dEncodeFunctions[ types.TupleType ] = encodeTuple
g_dDecodeFunctions[ "t" ] = decodeTuple

#Encode and decode a dictionary
def encodeDict( dValue, eList ):
  eList.append( "d" )
  for key in sorted( dValue ):
    g_dEncodeFunctions[ type( key ) ]( key, eList )
    g_dEncodeFunctions[ type( dValue[key] ) ]( dValue[key], eList )
  eList.append( "e" )

def decodeDict( data, i ):
  oD = {}
  i += 1
  while data[ i ] != "e":
    k, i = g_dDecodeFunctions[ data[ i ] ]( data, i )
    oD[ k ], i = g_dDecodeFunctions[ data[ i ] ]( data, i )
  return ( oD, i + 1 )

g_dEncodeFunctions[ types.DictType ] = encodeDict
g_dDecodeFunctions[ "d" ] = decodeDict

################################################################################
#                  New code for JSON (un)marshalling                           #
################################################################################
def hintParticularTypes( item ):
    """This function detects tuples and longs and replaces them with dictionaries.
    This allows us to prserve these data types. By default, 'json.dumps()' encodes
    tuples into arrays, (like python lists) and longs into int numbers
    (like python ints). By using directly 'json.loads()', without
    'DEncode.hintParticularTypes()', arrays are decoded into lists (so we
    lose our tuples) and int numbers into ints (then we also lose long ints)."""

    if isinstance( item, tuple ):
        L = []
        for i in item:
            L.append( hintParticularTypes( i ) )
        newTuple = tuple( L )
        return {'__tuple__': True, 'items': newTuple}
    elif isinstance( item, long ):
        return {'__long__': True, 'value': item}
    elif isinstance( item, list ):
        return [hintParticularTypes(e) for e in item]
    elif isinstance( item, dict ):
        newDict = {}
        for key in item:
            newDict[key] = hintParticularTypes( item[key] )
        return newDict
    elif isinstance( item, _dateTimeType ):
        dateTimeTuple = ( item.year, item.month, item.day, item.hour,
                          item.minute, item.second,
                          item.microsecond, item.tzinfo )
        return {'__dateTime__':True, 'items':dateTimeTuple}
    elif isinstance(item, _dateType):
        dateTuple = ( item.year, item.month, item. day )
        return {"__date__":True, 'items':dateTuple}
    elif isinstance(item, _timeType):
        timeTuple = ( item.hour, item.minute, item.second, item.microsecond, item.tzinfo )
        return {"__time__":True, 'items':timeTuple}
    else:
        return item

def DetectHintedParticularTypes( object ):
    """This function detecs dictionaries encoding tuples and longs and replaces
    them with the correct data structures. """
    newTuple = tuple()
    if isinstance(object, list):
        return [DetectHintedParticularTypes(e) for e in object]
    elif isinstance( object, dict ):
        if '__tuple__' in object:
            newTuple = DetectHintedParticularTypes( object['items'] )
            return tuple(newTuple)
        elif '__long__' in object:
            return long( object['value'] )
        elif '__dateTime__' in object:
            L = list()
            for i in object['items']:
                L.append(i)
            newTuple = tuple(L)
            return datetime.datetime(*newTuple)
        elif '__date__' in object:
            L = list()
            for i in object['items']:
                L.append(i)
            newTuple = tuple(L)
            return datetime.date(*newTuple)
        elif '__time__' in object:
            L = list()
            for i in object['items']:
                L.append(i)
            newTuple = tuple(L)
            return datetime.time(*newTuple)
        else:
            newDict = {}
            for key in object:
                newDict[key] = DetectHintedParticularTypes( object[key] )
            return newDict
    elif isinstance(object, tuple):
        L = list()
        for i in object:
            L.append( DetectHintedParticularTypes( i ) )
        newTuple = tuple( L )
        return newTuple
    else:
        return object

class newEncoder(json.JSONEncoder):
    def encode( self, object ):
        return super( newEncoder, self ).encode( hintParticularTypes( object ) )

#################################################################################
# The choice between DEncode and JSON is made by the "protocol" argument passed #
# to the 'encode()' and 'decode()' functions. This argument is set to "DEncode" #
# by default. If the (un)marshalling must be performed in JSON, then the        #
# 'encode()' and 'decode()' functions must be called with the "protocol"        #
# argument set to "JSON".                                                       #
#################################################################################
def encode( uObject, protocol = "DEncode" ):

    if protocol == "JSON":
        ########################################################################
        #                            We can use JSON                           #
        ########################################################################
        coding = newEncoder()                                                  #
        serializedString = coding.encode( uObject )                            #
        return serializedString                                                #
        ########################################################################

    else:
        ########################################################################
        #                      or we can stay with DEncode                     #
        ########################################################################
        try:                                                                   #
            eList = []                                                         #
            #print "ENCODE FUNCTION : %s" % g_dEncodeFunctions[ type( uObject ) ]
            g_dEncodeFunctions[ type( uObject ) ]( uObject, eList )            #
            return "".join( eList )                                            #
        except Exception:                                                      #
            raise                                                              #
        ########################################################################

def decode( data, protocol = "DEncode" ):

    if protocol == "JSON":
        ########################################################################
        #                            We can use JSON                           #
        ########################################################################
        return json.loads( data, object_hook =  DetectHintedParticularTypes )  #
        ########################################################################

    else:
        ########################################################################
        #                      or we can stay with DEncode                     #
        ########################################################################
        if not data:                                                           #
            return data                                                        #
        try:                                                                   #
            #print "DECODE FUNCTION : %s" % g_dDecodeFunctions[ sStream [ iIndex ] ]
            return g_dDecodeFunctions[ data[ 0 ] ]( data, 0 )                  #
        except Exception:                                                      #
            raise                                                              #
        ########################################################################

#if __name__ == "__main__":
    #test_tuple = (1,2,3)
    #dict_tuple = {'__tuple__': True, 'items': test_tuple}
    #test_long = long(6)
    #dict_long = {'__long__': True, 'value': test_long}
    #test_list = [test_tuple, test_long]
    #test_dict = {'t':test_tuple, 'l':test_long}

    #print "test_dict = {}".format(test_dict)
    #d = encode(test_dict)
    #print "encoded dict = {}".format(d)
    #D = decode(d)
    #print "decoded dict = {}".format(D)
