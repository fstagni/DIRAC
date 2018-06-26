from DIRAC.Core.Base.Client import Client

class AtomClient(Client):

  def __init__( self, **kwargs ):
    """ Simple constructor
    """

    Client.__init__( self, **kwargs )
    self.setServer( 'Framework/Atom' )

  def setServer( self, url ):
    self.serverURL = url
