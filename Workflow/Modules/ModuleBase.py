''' ModuleBase - contains the base class for workflow modules. Defines several common utility methods
'''

import os, copy

from DIRAC                                                  import S_OK, S_ERROR, gLogger
from DIRAC.ConfigurationSystem.Client.Helpers.Operations    import Operations
from DIRAC.WorkloadManagementSystem.Client.JobReport        import JobReport
from DIRAC.TransformationSystem.Client.FileReport           import FileReport
from DIRAC.RequestManagementSystem.Client.RequestContainer  import RequestContainer
from DIRAC.DataManagementSystem.Client.ReplicaManager       import ReplicaManager


class ModuleBase( object ):
  ''' Base class for Modules - works only within DIRAC workflows
  '''

  #############################################################################

  def __init__( self, loggerIn = None, operationsHelperIn = None, rm = None ):
    ''' Initialization of module base.
    '''

    if not loggerIn:
      self.log = gLogger.getSubLogger( 'ModuleBase' )
    else:
      self.log = loggerIn

    if not operationsHelperIn:
      self.opsH = Operations()
    else:
      self.opsH = operationsHelperIn

    if not rm:
      self.rm = ReplicaManager()
    else:
      self.rm = rm

    self.production_id = ''
    self.prod_job_id = ''
    self.jobID = ''
    self.step_number = ''
    self.step_id = ''

    self.workflowStatus = None
    self.stepStatus = None
    self.workflow_commons = None
    self.step_commons = None

  #############################################################################

  def execute( self, production_id = None, prod_job_id = None, wms_job_id = None,
               workflowStatus = None, stepStatus = None,
               wf_commons = None, step_commons = None,
               step_number = None, step_id = None ):
    ''' Function called by all super classes
    '''

    if production_id:
      self.production_id = production_id
    else:
      self.production_id = self.PRODUCTION_ID

    if prod_job_id:
      self.prod_job_id = prod_job_id
    else:
      self.prod_job_id = self.JOB_ID

    if os.environ.has_key( 'JOBID' ):
      self.jobID = os.environ['JOBID']

    if wms_job_id:
      self.jobID = wms_job_id

    if workflowStatus:
      self.workflowStatus = workflowStatus

    if stepStatus:
      self.stepStatus = stepStatus

    if wf_commons:
      self.workflow_commons = wf_commons

    if step_commons:
      self.step_commons = step_commons

    if step_number:
      self.step_number = step_number
    else:
      self.step_number = self.STEP_NUMBER

    if step_id:
      self.step_id = step_id
    else:
      self.step_id = '%s_%s_%s' % ( self.production_id, self.prod_job_id, self.step_number )

    try:
      # This is what has to be extended in the modules
      self._resolveInputVariables()
      self._initialize()
      self._setCommand()
      self._executeCommand()
      self._execute()
      return self._finalize()

    except GracefulTermination, e:
      self.log.info( e )
      return S_OK( e )

    except Exception, e:
      self.log.error( e )
      return S_ERROR( e )

    finally:
      self.finalize()

  def _initialize( self ):
    ''' TBE '''
    pass

  def _setCommand( self ):
    ''' TBE '''
    self.command = None

  def _executeCommand( self ):
    ''' TBE '''
    pass

  def _execute( self ):
    ''' TBE '''
    return S_OK()

  def _finalize( self ):
    ''' TBE '''
    raise GracefulTermination, 'Correctly finalized'

  #############################################################################

  def finalize( self ):
    ''' Just finalizing the module execution
    '''

    self.log.flushAllMessages( 0 )
    self.log.info( '===== Terminating ' + str( self.__class__ ) + ' ===== ' )

  #############################################################################

  def _resolveInputVariables( self ):
    ''' By convention the module input parameters are resolved here.
    '''

    self.log.verbose( "workflow_commons = ", self.workflow_commons )
    self.log.verbose( "step_commons = ", self.step_commons )

    self.fileReport = self._getFileReporter()
    self.jobReport = self._getJobReporter()
    self.request = self._getRequestContainer()

    self._resolveInputWorkflow()

  #############################################################################

  def _getJobReporter( self ):
    ''' just return the job reporter (object, always defined by dirac-jobexec)
    '''

    if self.workflow_commons.has_key( 'JobReport' ):
      return self.workflow_commons['JobReport']
    else:
      jobReport = JobReport( self.jobID )
      self.workflow_commons['JobReport'] = jobReport
      return jobReport

  #############################################################################

  def _getFileReporter( self ):
    ''' just return the file reporter (object)
    '''

    if self.workflow_commons.has_key( 'FileReport' ):
      return self.workflow_commons['FileReport']
    else:
      fileReport = FileReport()
      self.workflow_commons['FileReport'] = fileReport
      return fileReport

  #############################################################################

  def _getRequestContainer( self ):
    ''' just return the RequestContainer reporter (object)
    '''

    if self.workflow_commons.has_key( 'Request' ):
      return self.workflow_commons['Request']
    else:
      request = RequestContainer()
      self.workflow_commons['Request'] = request
      return request

  #############################################################################

  def _resolveInputWorkflow( self ):
    ''' Resolve the input variables that are in the workflow_commons
    '''

    if self.workflow_commons.has_key( 'JobType' ):
      self.jobType = self.workflow_commons['JobType']

    self.InputData = ''
    if self.workflow_commons.has_key( 'InputData' ):
      if self.workflow_commons['InputData']:
        self.InputData = self.workflow_commons['InputData']

    if self.workflow_commons.has_key( 'ParametricInputData' ):
      pID = copy.deepcopy( self.workflow_commons['ParametricInputData'] )
      if pID:
        if type( pID ) == type( [] ):
          pID = ';'.join( pID )
  #      self.InputData += ';' + pID
        self.InputData = pID
        self.InputData = self.InputData.rstrip( ';' )

    if self.InputData == ';':
      self.InputData = ''

    if self.workflow_commons.has_key( 'outputDataFileMask' ):
      self.outputDataFileMask = self.workflow_commons['outputDataFileMask']
      if not type( self.outputDataFileMask ) == type( [] ):
        self.outputDataFileMask = [i.lower().strip() for i in self.outputDataFileMask.split( ';' )]

  #############################################################################

  def _resolveInputStep( self ):
    ''' Resolve the input variables for an application step
    '''

    self.stepName = self.step_commons['STEP_INSTANCE_NAME']

    if self.step_commons.has_key( 'executable' ) and self.step_commons['executable']:
      self.executable = self.step_commons['executable']
    else:
      self.executable = 'Unknown'

    if self.step_commons.has_key( 'applicationName' ) and self.step_commons['applicationName']:
      self.applicationName = self.step_commons['applicationName']
    else:
      self.applicationName = 'Unknown'

    if self.step_commons.has_key( 'applicationVersion' ) and self.step_commons['applicationVersion']:
      self.applicationVersion = self.step_commons['applicationVersion']
    else:
      self.applicationVersion = 'Unknown'

    if self.step_commons.has_key( 'applicationLog' ):
      self.applicationLog = self.step_commons['applicationLog']

    stepInputData = []
    if self.step_commons.has_key( 'inputData' ):
      if self.step_commons['inputData']:
        stepInputData = self.step_commons['inputData']
    elif self.InputData:
      stepInputData = copy.deepcopy( self.InputData )
    if stepInputData:
      stepInputData = self._determineStepInputData( stepInputData, )
      self.stepInputData = [sid.strip( 'LFN:' ) for sid in stepInputData]

  #############################################################################

  def _determineStepInputData( self, inputData ):
    ''' determine the input data for the step
    '''
    if inputData == 'previousStep':
      stepIndex = self.gaudiSteps.index( self.stepName )
      previousStep = self.gaudiSteps[stepIndex - 1]

      stepInputData = []
      for outputF in self.workflow_commons['outputList']:
        try:
          if outputF['stepName'] == previousStep and outputF['outputDataType'].lower() == self.inputDataType.lower():
            stepInputData.append( outputF['outputDataName'] )
        except KeyError:
          return S_ERROR( 'Can\'t find output of step %s' % previousStep )

      return stepInputData

    else:
      return [x.strip( 'LFN:' ) for x in inputData.split( ';' )]

  #############################################################################

  def setApplicationStatus( self, status, sendFlag = True, jr = None ):
    '''Wraps around setJobApplicationStatus of state update client
    '''
    if not self._WMSJob():
      return S_OK( 'JobID not defined' )  # e.g. running locally prior to submission

    self.log.verbose( 'setJobApplicationStatus(%s, %s)' % ( self.jobID, status ) )

    if not jr:
      jr = self._getJobReporter()

    jobStatus = jr.setApplicationStatus( status, sendFlag )
    if not jobStatus['OK']:
      self.log.warn( jobStatus['Message'] )

    return jobStatus

  #############################################################################

  def _WMSJob( self ):
    ''' Check if this job is running via WMS
    '''
    if not self.jobID:
      return False
    else:
      return True

  #############################################################################

  def _enableModule( self ):
    ''' Enable module if it's running via WMS
    '''
    if not self._WMSJob():
      self.log.info( 'No WMS JobID found, disabling module via control flag' )
      return False
    else:
      self.log.verbose( 'Found WMS JobID = %s' % self.jobID )
      return True

  #############################################################################

  def _checkWFAndStepStatus( self, noPrint = False ):
    ''' Check the WF and Step status
    '''
    if not self.workflowStatus['OK'] or not self.stepStatus['OK']:
      if not noPrint:
        self.log.info( 'Skip this module, failure detected in a previous step :' )
        self.log.info( 'Workflow status : %s' % ( self.workflowStatus ) )
        self.log.info( 'Step Status : %s' % ( self.stepStatus ) )
      return False
    else:
      return True

  #############################################################################

  def setJobParameter( self, name, value, sendFlag = True, jr = None ):
    '''Wraps around setJobParameter of state update client
    '''
    if not self._WMSJob():
      return S_OK( 'JobID not defined' )  # e.g. running locally prior to submission

    self.log.verbose( 'setJobParameter(%s,%s,%s)' % ( self.jobID, name, value ) )

    if not jr:
      jr = self._getJobReporter()

    jobParam = jr.setJobParameter( str( name ), str( value ), sendFlag )
    if not jobParam['OK']:
      self.log.warn( jobParam['Message'] )

    return jobParam

  #############################################################################

  def setFileStatus( self, production, lfn, status, fileReport = None ):
    ''' set the file status for the given production in the Transformation Database
    '''
    self.log.verbose( 'setFileStatus(%s,%s,%s)' % ( production, lfn, status ) )

    if not fileReport:
      fileReport = self._getFileReporter()

    fileReport.setFileStatus( production, lfn, status )

  #############################################################################


  def getCandidateFiles( self, outputList, outputLFNs, fileMask, stepMask = '' ):
    ''' Returns list of candidate files to upload, check if some outputs are missing.

        outputList has the following structure:
          [ {'outputDataType':'','outputDataSE':'','outputDataName':''} , {...} ]

        outputLFNs is the list of output LFNs for the job

        fileMask is the output file extensions to restrict the outputs to

        returns dictionary containing type, SE and LFN for files restricted by mask
    '''
    fileInfo = {}

    for outputFile in outputList:
      if outputFile.has_key( 'outputDataType' ) \
      and outputFile.has_key( 'outputDataSE' ) \
      and outputFile.has_key( 'outputDataName' ):
        fname = outputFile['outputDataName']
        fileSE = outputFile['outputDataSE']
        fileType = outputFile['outputDataType']
        fileInfo[fname] = {'type':fileType, 'workflowSE':fileSE}
      else:
        self.log.error( 'Ignoring malformed output data specification', str( outputFile ) )

    for lfn in outputLFNs:
      if os.path.basename( lfn ) in fileInfo.keys():
        fileInfo[os.path.basename( lfn )]['lfn'] = lfn
        self.log.verbose( 'Found LFN %s for file %s' % ( lfn, os.path.basename( lfn ) ) )

    # check local existance
    try:
      self._checkLocalExistance( fileInfo.keys() )
    except OSError:
      return S_ERROR( 'Output Data Not Found' )

    # Select which files have to be uploaded: in principle all
    candidateFiles = self._applyMask( fileInfo, fileMask, stepMask )

    # Sanity check all final candidate metadata keys are present (return S_ERROR if not)
    try:
      self._checkSanity( candidateFiles )
    except ValueError:
      return S_ERROR( 'Missing requested fileName keys' )

    return S_OK( candidateFiles )

  #############################################################################

  def _applyMask( self, candidateFilesIn, fileMask, stepMask ):
    ''' Select which files have to be uploaded: in principle all
    '''
    candidateFiles = copy.deepcopy( candidateFilesIn )

    if type( fileMask ) != type( [] ):
      fileMask = [fileMask]

    if fileMask and fileMask != ['']:
      for fileName, metadata in candidateFiles.items():
        if ( ( metadata['type'].lower() not in fileMask ) ):  # and ( fileName.split( '.' )[-1] not in fileMask ) ):
          del( candidateFiles[fileName] )
          self.log.info( 'Output file %s was produced but will not be treated (fileMask is %s)' % ( fileName,
                                                                                              ', '.join( fileMask ) ) )
    else:
      self.log.info( 'No outputDataFileMask provided, the files with all the extensions will be considered' )

    if stepMask:
      for fileName, metadata in candidateFiles.items():
        if fileName.split( '_' )[-1].split( '.' )[0] not in stepMask:
          del( candidateFiles[fileName] )
          self.log.info( 'Output file %s was produced but will not be treated (stepMask is %s)' % ( fileName,
                                                                                              ', '.join( stepMask ) ) )
    else:
      self.log.info( 'No outputDataStep provided, the files output of all the steps will be considered' )

    return candidateFiles

  #############################################################################

  def _checkSanity( self, candidateFiles ):
    ''' Sanity check all final candidate metadata keys are present
    '''

    notPresentKeys = []

    mandatoryKeys = ['type', 'workflowSE', 'lfn']  # filedict is used for requests
    for fileName, metadata in candidateFiles.items():
      for key in mandatoryKeys:
        if not metadata.has_key( key ):
          notPresentKeys.append( ( fileName, key ) )

    if notPresentKeys:
      for fileName_keys in notPresentKeys:
        self.log.error( 'File %s has missing %s' % ( fileName_keys[0], fileName_keys[1] ) )
      raise ValueError

  #############################################################################

  def _checkLocalExistance( self, fileList ):
    ''' Check that the list of output files are present locally
    '''

    notPresentFiles = []

    for fileName in fileList:
      if not os.path.exists( fileName ):
        notPresentFiles.append( fileName )

    if notPresentFiles:
      self.log.error( 'Output data file list %s does not exist locally' % notPresentFiles )
      raise os.error

  #############################################################################

#############################################################################

class GracefulTermination(Exception):
  pass

#############################################################################
