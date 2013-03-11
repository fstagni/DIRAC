''' The Script class provides a simple way for users to specify an executable
    or file to run (and is also a simple example of a workflow module).
'''

import os, sys, re

from DIRAC.Core.Utilities.Subprocess    import shellCall
from DIRAC                              import gLogger, S_OK, S_ERROR

from DIRAC.Workflow.Modules.ModuleBase  import ModuleBase

class Script( ModuleBase ):

  #############################################################################
  def __init__( self, rm = None ):
    ''' c'tor
    '''
    self.log = gLogger.getSubLogger( 'Script' )
    super( Script, self ).__init__( self.log, rm = rm )

    # Set defaults for all workflow parameters here
    self.name = ''
    self.executable = ''
    self.logFile = ''
    self.arguments = ''
    self.step_commons = {}

  #############################################################################

  def resolveInputVariables( self ):
    ''' By convention the workflow parameters are resolved here.
    '''
    super( Script, self )._resolveInputVariables()
    super( Script, self )._resolveInputStep()

    if self.step_commons.has_key( 'name' ):
      self.name = self.step_commons['name']
    else:
      result = S_ERROR( 'No module instance name defined' )
      self.log.warn( 'No module instance name defined' )

    if self.step_commons.has_key( 'executable' ):
      self.executable = self.step_commons['executable']
    else:
      result = S_ERROR( 'No executable defined' )
      self.log.warn( 'No executable defined' )

    if self.step_commons.has_key( 'logFile' ):
      self.logFile = self.step_commons['logFile']
    else:
      result = S_ERROR( 'No logFile defined' )
      self.log.warn( 'No logFile defined' )

    if self.step_commons.has_key( 'arguments' ):
      self.arguments = self.step_commons['arguments']

  #############################################################################

  def execute( self, production_id = None, prod_job_id = None, wms_job_id = None,
               workflowStatus = None, stepStatus = None,
               wf_commons = None, step_commons = None,
               step_number = None, step_id = None ):
    ''' Main execution method.
    '''

    try:
      super( Script, self ).execute( production_id, prod_job_id, wms_job_id,
                                     workflowStatus, stepStatus,
                                     wf_commons, step_commons,
                                     step_number, step_id )

      self._resolveInputVariables()

      self.log.info( 'Script Module Instance Name: %s' % ( self.name ) )
      cmd = self.executable
      if os.path.exists( os.path.basename( self.executable ) ):
        self.executable = os.path.basename( self.executable )
        if not os.access( '%s/%s' % ( os.getcwd(), self.executable ), 5 ):
          os.chmod( '%s/%s' % ( os.getcwd(), self.executable ), 0755 )
        cmd = '%s/%s' % ( os.getcwd(), self.executable )
      if re.search( '.py$', self.executable ):
        cmd = '%s %s' % ( sys.executable, self.executable )
      if self.arguments:
        cmd = '%s %s' % ( cmd, self.arguments )

      self.log.info( 'Command is: %s' % cmd )
      outputDict = shellCall( 0, cmd )
      if not outputDict['OK']:
        failed = True
        self.log.error( 'Shell call execution failed:' )
        self.log.error( outputDict['Message'] )
      resTuple = outputDict['Value']
      status = resTuple[0]
      stdout = resTuple[1]
      stderr = resTuple[2]
      if status:
        failed = True
        self.log.error( 'Non-zero status %s while executing %s' % ( status, cmd ) )
      else:
        self.log.info( '%s execution completed with status %s' % ( self.executable, status ) )

      self.log.verbose( stdout )
      self.log.verbose( stderr )
      if os.path.exists( self.logFile ):
        self.log.verbose( 'Removing existing %s' % self.logFile )
        os.remove( self.logFile )
      fopen = open( '%s/%s' % ( os.getcwd(), self.logFile ), 'w' )
      fopen.write( '<<<<<<<<<< %s Standard Output >>>>>>>>>>\n\n%s ' % ( self.executable, stdout ) )
      if stderr:
        fopen.write( '<<<<<<<<<< %s Standard Error >>>>>>>>>>\n\n%s ' % ( self.executable, stderr ) )
      fopen.close()
      self.log.info( 'Output written to %s, execution complete.' % ( self.logFile ) )

      if failed:
        return S_ERROR( 'Exit Status %s' % ( status ) )

      return S_OK()

    except Exception, e:
      self.log.exception( e )
      return S_ERROR( e )

    finally:
      super( Script, self ).finalize()


# EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#
