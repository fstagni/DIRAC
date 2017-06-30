# $HeadURL$

###############################################################################
#                           DEncode2.py                                       #
###############################################################################
__RCSID__ = "$Id$"

import json

def hintParticularTypes( item ):
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
    else:
        return item

def hintedParticularTypes( object ):
    if '__tuple__' in object:
        newTuple = hintedParticularTypes( object['items'] )
        return tuple( newTuple )
    elif '__long__' in object:
        return long( object['value'] )
    else:
        return object

class newEncoder(json.JSONEncoder):
    def encode( self, object ):
        return super( newEncoder, self ).encode( hintParticularTypes( object ) )

def encode( data ):
    coding = newEncoder()
    serializedString = coding.encode( data )
    return serializedString

def decode( encodedString ):
    return json.loads( encodedString, object_hook =  hintedParticularTypes )

if __name__ == "__main__":
    pass
