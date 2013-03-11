import unittest

from DIRAC.Core.Workflow.Parameter import Parameter
from mock import Mock
from DIRAC.Core.Workflow.Module import ModuleDefinition
from DIRAC.Core.Workflow.Step import StepDefinition
# from DIRAC.Interfaces.API.Job import Job
from DIRAC.Workflow.Utilities.Utils import getStepDefinition, getStepCPUTimes

#############################################################################

class UtilitiesTestCase( unittest.TestCase ):
  """ Base class
  """
  def setUp( self ):

#    self.job = Job()
    pass

class UtilsSuccess( UtilitiesTestCase ):

  def test__getStepDefinition( self ):
    importLine = """
 from DIRAC.Workflow.Modules.<MODULE> import <MODULE>
 """
    # modules
    gaudiApp = ModuleDefinition( 'Script' )
    gaudiApp.setDescription( 'Script class' )
    body = importLine.replace( '<MODULE>', 'Script' )
    gaudiApp.setBody( body )

    genBKReport = ModuleDefinition( 'BookkeepingReport' )
    genBKReport.setDescription( 'Bookkeeping Report class' )
    body = importLine.replace( '<MODULE>', 'BookkeepingReport' )
    genBKReport.setBody( body )

    # step
    gaudiAppDefn = StepDefinition( 'Gaudi_App_Step' )
    gaudiAppDefn.addModule( gaudiApp )
    gaudiAppDefn.createModuleInstance( 'Script', 'Script' )
    gaudiAppDefn.addModule( genBKReport )
    gaudiAppDefn.createModuleInstance( 'BookkeepingReport', 'BookkeepingReport' )

    gaudiAppDefn.addParameterLinked( gaudiApp.parameters )

    stepDef = getStepDefinition( 'Gaudi_App_Step', ['GaudiApplication', 'BookkeepingReport'] )
    self.assert_( str( gaudiAppDefn ) == str( stepDef ) )

    self.job._addParameter( gaudiAppDefn, 'name', 'type', 'value', 'desc' )
    self.job._addParameter( gaudiAppDefn, 'name1', 'type1', 'value1', 'desc1' )


    stepDef = getStepDefinition( 'Gaudi_App_Step', ['GaudiApplication', 'BookkeepingReport'],
                                 parametersList = [[ 'name', 'type', 'value', 'desc' ],
                                                   [ 'name1', 'type1', 'value1', 'desc1' ]] )


    self.assert_( str( gaudiAppDefn ) == str( stepDef ) )

  def test_getStepCPUTimes( self ):
    execT, cpuT = getStepCPUTimes( {} )
    self.assertEqual( execT, 0 )
    self.assertEqual( cpuT, 0 )
    execT, cpuT = getStepCPUTimes( {'StartTime':0, 'StartStats': ( 0, 0, 0, 0, 0 )} )
    print execT, cpuT

if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase( UtilitiesTestCase )
  suite.addTest( unittest.defaultTestLoader.loadTestsFromTestCase( UtilsSuccess ) )
  testResult = unittest.TextTestRunner( verbosity = 2 ).run( suite )

