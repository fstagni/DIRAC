from DIRAC import S_OK, S_ERROR, gConfig

from DIRAC.Core.Utilities.Subprocess                     import systemCall, pythonCall
import os

class MyDIRACObject( object ):

  def __init__( self ):
    print 'in MyDIRACObject', gConfig.getValue( '/LocalSite/cfg', 'NOTSET' )

    payloadEnv = dict( os.environ )
#     result = systemCall( 0, ( 'ls', '-al', '--color' ), callbackFunction = self.sendOutput, env = payloadEnv )

    result = systemCall( 0, ( '/home/toffo/LHCbCode/DIRAC/FrameworkSystem/scripts/myDIRACScript.py', '/home/toffo/LHCbCode/etc/myTestCFG.cfg' ), callbackFunction = self.sendOutput, env = payloadEnv )
#     result = systemCall( 0, ( '/home/toffo/LHCbCode/DIRAC/FrameworkSystem/scripts/myDIRACScript.py', '-o', '/LocalSite/cfg=pippo' ), callbackFunction = self.sendOutput, env = payloadEnv )
#     result = systemCall( 0, '/home/toffo/LHCbCode/DIRAC/FrameworkSystem/scripts/myDIRACScript.py /home/toffo/LHCbCode/etc/myTestCFG.cfg', callbackFunction = self.sendOutput, env = payloadEnv )
#     result = systemCall( 0, 'myDIRACScript.py' )
    print result
    
#     result = pythonCall( 0, '/home/toffo/LHCbCode/DIRAC/FrameworkSystem/scripts/myDIRACScript.py' )
#     print result
    
  def sendOutput(self, stdid, line):
    """ Callback function such that the results from the CE may be returned.
    """
    print line
