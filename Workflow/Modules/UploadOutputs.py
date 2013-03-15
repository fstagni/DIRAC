''' Module to upload specified job output files according to the parameters
    defined in the production workflow.
'''

import os, sys, re

from DIRAC.Core.Utilities.Subprocess    import shellCall
from DIRAC                              import gLogger

from DIRAC.Workflow.Modules.ModuleBase  import ModuleBase, GracefulTermination

class UploadOutputs( ModuleBase ):

  #############################################################################

  def __init__( self, rm = None ):
    ''' c'tor
    '''
    self.log = gLogger.getSubLogger( "UploadOutputs" )
    super( UploadOutputs, self ).__init__( self.log, rm = rm )

  #############################################################################

  def _resolveInputVariables( self ):
    ''' By convention the module parameters are resolved here.
    '''

    super( UploadOutputs, self )._resolveInputVariables()

  def _initialize(self):
    ''' gets the files to upload, check if to upload
    '''
    pass

  def _execute(self):
    ''' uploads the files
    '''
    pass
