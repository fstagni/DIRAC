""" :mod: SimplestAgent

    Simplest Agent send a simple log message
"""

# # imports
from DIRAC import S_OK, S_ERROR, gConfig
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.DISET.RPCClient import RPCClient

from DIRAC.FrameworkSystem.Client.MyDIRACObject import MyDIRACObject

from DIRAC.ConfigurationSystem.Client.ConfigurationData import gConfigurationData


__RCSID__ = "Id: $"

class SimplestAgent( AgentModule ):
  """
  .. class:: SimplestAgent

  Simplest agent
  print a message on log
  """

  def pippo( self ):
    print 'AAAAAA'

  def initialize( self ):
    """ agent's initalisation

    :param self: self reference
    """
#     self.message = self.am_getOption( 'Message', "SimplestAgent is working..." )
#     self.log.info( "message = %s" % self.message )

    # print "gConfigurationData.mergedCFG", gConfigurationData.mergedCFG
    print 'in initialize', gConfig.getValue( '/LocalSite/cfg', 'NOTSET' )
    mdo = MyDIRACObject()


    return S_OK()

  def execute( self ):
    """ execution in one agent's cycle

    :param self: self reference
    """
#     self.log.info( "message is: %s" % self.message )
#     simpleMessageService = RPCClient( 'Framework/Hello' )
#     result = simpleMessageService.sayHello( self.message )
#     if not result['OK']:
#       self.log.error( "Error while calling the service: %s" % result['Message'] )
#       return result
#     self.log.info( "Result of the request is %s" % result[ 'Value' ] )

    gConfigurationData.setOptionInCFG( '/LocalSite/cfg', 'NOW_ITS_SET' )
    print 'in execute', gConfig.getValue( '/LocalSite/cfg', 'NOTSET' )
    mdo = MyDIRACObject()


#     print "gConfigurationData.mergedCFG", gConfigurationData.mergedCFG



    return S_OK()

