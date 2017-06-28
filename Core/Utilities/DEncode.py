# $HeadURL$

###############################################################################
#                           DEncode.py                                        #
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

import pdb
import datetime
import json
import types

_dateTimeObject = datetime.datetime.utcnow()
_dateTimeType = type( _dateTimeObject )
_dateType = type( _dateTimeObject.date() )
_timeType = type( _dateTimeObject.time() )

g_dEncodeFunctions = {}
g_dDecodeFunctions = {}

class newEncoder(json.JSONEncoder):
    def encode(self, object):
        def hintParticularTypes(item):
            if isinstance(item, tuple):
                return {'__tuple__': True, 'items': item}
            elif isinstance(item, long):
                return {'__long__': True, 'value': item}
            elif isinstance(item, list):
                return [hintParticularTypes(e) for e in item]
            elif isinstance(item, dict):
                newDict = {}
                for key in item:
                    newDict[key] = hintParticularTypes(item[key])
                return newDict
            else:
                return item

        return super(newEncoder, self).encode(hintParticularTypes(object))

def hintedParticularTypes(object):
    if '__tuple__' in object:
        return tuple(object['items'])
    elif '__long__' in object:
        return long(object['value'])


def genericEncoding( data ):
    return json.dumps( data )

g_dEncodeFunctions[ float ] = genericEncoding
g_dEncodeFunctions[ bool ] = genericEncoding
g_dEncodeFunctions[ types.NoneType ] = genericEncoding

#def genericDecoding( data ):
    #return json.loads( data )

#Encoding and decoding ints
def encodeInt( intToSerialize ):
    eDict = dict()
    eDict['__type__'] = 'i'
    eDict['__value__'] = intToSerialize
    return json.dumps( eDict )

def decodeInt( dictionary ):
    return int( dictionary['__value__'] )

g_dEncodeFunctions[ int ] = encodeInt
g_dDecodeFunctions[ "i" ] = decodeInt

#Encoding and decoding longs
def encodeLong( iValue ):
    eDict = dict()
    eDict['__type__'] = 'I'
    eDict['__value__'] = iValue
    return json.dumps(eDict)

def decodeLong( iDict ):
    return long( iDict['__value__'] )

g_dEncodeFunctions[ long ] = encodeLong
g_dDecodeFunctions[ "I" ] = decodeLong

#Encoding and decoding strings
def encodeString( sValue ):
    eDict = dict()
    eDict['__type__'] = 's'
    eDict['__value__'] = sValue
    return json.dumps(eDict)

def decodeString( iDict ):
    return str( iDict['__value__'] )

g_dEncodeFunctions[ str ] = encodeString
g_dDecodeFunctions[ "s" ] = decodeString

#Encoding and decoding unicode strings
#def encodeUnicode( sValue ):
    #eDict = dict()
    #eDict['__type__'] = 'u'
    #eDict['__value__'] = sValue
    #return json.dumps(eDict)

#def decodeUnicode( iDict ):
    #return unicode( iDict['__value__'] )

g_dEncodeFunctions[ unicode ] = genericEncoding
#g_dDecodeFunctions[ "u" ] = decodeUnicode

#Encoding and decoding datetime
def encodeDateTime( oValue ):
    eDict = dict()
    if type( oValue ) == _dateTimeType:
        eDict['__value__'] = ( oValue.year, oValue.month, oValue.day,
                               oValue.hour, oValue.minute, oValue.second,
                               oValue.microsecond, oValue.tzinfo )
        eDict['__type__'] = 'za'
        return json.dumps(eDict)
    elif type( oValue ) == _dateType:
        eDict['__value__'] = ( oValue.year, oValue.month, oValue. day )
        eDict['__type__'] = 'zd'
        return json.dumps(eDict)
    elif type( oValue ) == _timeType:
        eDic['__value__'] = ( oValue.hour, oValue.minute, oValue.second,
                              oValue.microsecond, oValue.tzinfo )
        eDict['__type__'] = "zt"
        return json.dumps(eDict)
    else:
        raise Exception( "Unexpected type %s while encoding a datetime object"
                         % str( type( oValue ) ) )

def decodeDateTime( eDict ):
    if eDict['__type__'] == 'za':
        dtObject = datetime.datetime( eDict['__value__'] )
    elif eDict['__type__'] == 'zd':
        dtObject = datetime.date( eDict['__value__'] )
    elif eDict['__type__'] == 'zt':
        dtObject = datetime.time( eDict['__value__'] )
    else:
        raise Exception( "Unexpected type %s while decoding a datetime object"
                         % dataType )
    return ( dtObject )

g_dEncodeFunctions[ _dateTimeType ] = encodeDateTime
g_dEncodeFunctions[ _dateType ] = encodeDateTime
g_dEncodeFunctions[ _timeType ] = encodeDateTime
g_dDecodeFunctions[ 'za' ] = decodeDateTime
g_dDecodeFunctions[ 'zd' ] = decodeDateTime
g_dDecodeFunctions[ 'zt' ] = decodeDateTime

#Encode and decode a list
#def encodeList( listToSerialize ):
    #serializedList = list()
    #for element in listToSerialize:
        #serializedElement = g_dEncodeFunctions[type( element )]( element )
        #serializedList.append( serializedElement )
    #eDict = dict()
    #eDict['__type__'] = 'l'
    #eDict['__value__'] = serializedList
    #print eDict
    #return json.dumps(eDict)

#def decodeList( iDict ):
    #deserializedList = list( iDict['__value__'] )
    #for element in deserializedList:
        #element = decode( element )

g_dEncodeFunctions[ list ] = genericEncoding
#g_dDecodeFunctions[ "l" ] = decodeList

#Encode and decode a tuple
def encodeTuple( lValue ):
    listFromTuple = list()
    for element in lValue:
        listFromTuple.append( g_dEncodeFunctions[type( element )]( element ) )
    #for element in listFromTuple:
        #element = encode( element )
        #print( element )
    #print serialisedTuple
    eDict = dict()
    eDict['__type__'] = 't'
    eDict['__value__'] = listFromTuple
    return json.dumps(eDict)

def decodeTuple( iDict ):
    firstlist = list( iDict['__value__'] )
    for element in firstlist:
        element = decode( element )
    return tuple( firstlist )

g_dEncodeFunctions[ tuple ] = encodeTuple
g_dDecodeFunctions[ "t" ] = decodeTuple

def encodeDict( data ):
    for key in data:
        data[key] = encode( data[key] )
    return json.dumps( data )

def decodeDict( data ):
    for key in data:
        data[key] = decode( data[key] )
    return data

g_dEncodeFunctions[ dict ] = encodeDict
g_dDecodeFunctions[ "d" ] = decodeDict

#Encode function
def encode( data ):
    return g_dEncodeFunctions[ type( data ) ]( data )

def decode( encodedString ):
    deserializedData = json.loads( encodedString )
    try:
        deserializedDataType = deserializedData['__type__']
    except TypeError:
        return deserializedData
    except KeyError:
        deserializedData = decodeDict( deserializedData )
    else:
        deserializedData = g_dDecodeFunctions[ deserializedDataType ]( deserializedData )
        return deserializedData

if __name__ == "__main__":
    myTuple = ('t1', ('tt1','tt2'), ['l1','l2'])
    #pdb.set_trace()
    print decode(encode(myTuple)) == myTuple
    #gObject = {2:"3", True : ( 3, None ), 2.0 * 10 ** 20 : 2.0 * 10 ** -10 }
    #print "Initial: %s" % gObject
    #pdb.set_trace()
    #gData = encode( gObject )
    #print "Encoded: %s" % gData
    #print "Decoded: %s" % decode( gData )
