#!/usr/bin/env python
########################################################################
# $HeadURL$
# File :    dirac-distribution
# Author :  Adria Casajus
########################################################################
"""
  Create tarballs for a given DIRAC release
"""
__RCSID__ = "$Id$"

from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Base      import Script
from DIRAC.Core.Utilities import List, File, Distribution, Platform, Subprocess, CFG

import sys, os, re, urllib2, tempfile, getpass, ConfigParser

globalDistribution = Distribution.Distribution()

projectMapping = {
  'DIRAC' : "https://github.com/DIRACGrid/DIRAC/raw/master/releases.ini"
  }

class Params:

  def __init__( self ):
    self.releasesToBuild = []
    self.projectName = 'DIRAC'
    self.debug = False
    self.externalsBuildType = [ 'client' ]
    self.ignoreExternals = False
    self.forceExternals = False
    self.ignorePackages = False
    self.relini = False
    self.externalsPython = '26'
    self.destination = ""
    self.externalsLocation = ""
    self.makeJobs = 1

  def setReleases( self, optionValue ):
    self.releasesToBuild = List.fromChar( optionValue )
    return S_OK()

  def setProject( self, optionValue ):
    self.projectName = optionValue
    return S_OK()

  def setDebug( self, optionValue ):
    self.debug = True
    return S_OK()

  def setExternalsBuildType( self, optionValue ):
    self.externalsBuildType = List.fromChar( optionValue )
    return S_OK()

  def setForceExternals( self, optionValue ):
    self.forceExternals = True
    return S_OK()

  def setIgnoreExternals( self, optionValue ):
    self.ignoreExternals = True
    return S_OK()

  def setDestination( self, optionValue ):
    self.destination = optionValue
    return S_OK()

  def setPythonVersion( self, optionValue ):
    self.externalsPython = optionValue
    return S_OK()

  def setIgnorePackages( self, optionValue ):
    self.ignorePackages = True
    return S_OK()

  def setExternalsLocation( self, optionValue ):
    self.externalsLocation = optionValue
    return S_OK()

  def setMakeJobs( self, optionValue ):
    self.makeJobs = max( 1, int( optionValue ) )
    return S_OK()

  def setReleasesINI( self, optionValue ):
    self.relini = optionValue
    return S_OK()

  def registerSwitches( self ):
    Script.registerSwitch( "r:", "releases=", "releases to build (mandatory, comma separated)", cliParams.setReleases )
    Script.registerSwitch( "p:", "project=", "Project to build the release for (DIRAC by default)", cliParams.setProject )
    Script.registerSwitch( "D:", "destination", "Destination where to build the tar files", cliParams.setDestination )
    Script.registerSwitch( "i:", "pythonVersion", "Python version to use (25/26)", cliParams.setPythonVersion )
    Script.registerSwitch( "P", "ignorePackages", "Do not make tars of python packages", cliParams.setIgnorePackages )
    Script.registerSwitch( "C:", "relinit=", "Use <file> as the releases.ini", cliParams.setReleasesINI )
    Script.registerSwitch( "b", "buildExternals", "Force externals compilation even if already compiled", cliParams.setForceExternals )
    Script.registerSwitch( "B", "ignoreExternals", "Skip externals compilation", cliParams.setIgnoreExternals )
    Script.registerSwitch( "t:", "buildType=", "External type to build (client/server)", cliParams.setExternalsBuildType )
    Script.registerSwitch( "x:", "externalsLocation=", "Use externals location instead of downloading them", cliParams.setExternalsLocation )
    Script.registerSwitch( "j:", "makeJobs=", "Make jobs (default is 1)", cliParams.setMakeJobs )

    Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                        '\nUsage:',
                                        '  %s [option|cfgfile] ...\n' % Script.scriptName ] ) )

class ReleaseConfig:

  #Because python's INI parser is the utmost shittiest thing ever done
  class INI:
    def __init__( self, iniData ):
      self.__globalOps = {}
      self.__sections = {}
      self.__parse( iniData )

    def __parse( self, iniData ):
      secName = False
      for line in iniData.split( "\n" ):
        line = line.strip()
        if not line or line[0] in ( "#", ";" ):
          continue
        if line[0] == "[" and line[-1] == "]":
          secName = line[1:-1].strip()
          if secName not in self.__sections:
            self.__sections[ secName ] = {}
          continue
        tS = line.split( "=" )
        opName = tS[0].strip()
        opValue = "=".join( tS[1:] ).strip()
        if secName:
          self.__sections[ secName ][ opName ] = opValue
        else:
          self.__globalOps[ opName ] = opValue

    def isSection( self, secName ):
      return secName in self.__sections

    def get( self, opName, secName = False ):
      if secName:
        if secName not in self.__sections:
          return False
        if opName not in self.__sections[ secName ]:
          return False
        return self.__sections[ secName ][ opName ]
      #global op
      if opName not in self.__globalOps:
        return False
      return self.__globalOps[ opName ]

    def toString( self ):
      lines = [ "%s = %s" % ( opName, self.__globalOps[ opName ] ) for opName in self.__globalOps ] + [""]
      for secName in self.__sections:
        lines.append( "[%s]" % secName )
        lines += [ "   %s = %s" % ( opName, self.__sections[ secName ][ opName ] ) for opName in self.__sections[ secName ] ] + [ "" ]
      return "\n".join( lines )
  #END OF INI CLASS

  def __init__( self ):
    self.__configs = {}
    self.__projects = []

  def loadProject( self, projectName, releasesLocation = False ):
    if projectName in self.__projects:
      return True
    try:
      if releasesLocation:
        relFile = file( releasesLocation )
      else:
        releasesLocation = projectMapping[ projectName ]
        relFile = urllib2.urlopen( releasesLocation )
    except:
      gLogger.exception( "Could not open %s" % releasesLocation )
      return False
    try:
      config = ReleaseConfig.INI( relFile.read() )
    except:
      gLogger.exception( "Could not parse %s" % releasesLocation )
      return False
    relFile.close()
    gLogger.verbose( config.toString() )
    gLogger.notice( "Loaded %s" % releasesLocation )
    self.__projects.append( projectName )
    self.__configs[ projectName ] = config
    return True

  def __getOpt( self, projectName, option, section = False ):
    opVal = self.__configs[ projectName ].get( option, section )
    if not opVal:
      if section:
        gLogger.error( "Missing option %s/%s for project %s" % ( section, option, projectName ) )
      else:
        gLogger.error( "Missing option %s for project %s" % ( option, projectName ) )
      return False
    return opVal

  def getModulesForProjectRelease( self, projectName, releaseVersion ):
    if not projectName in self.__projects:
      gLogger.fatal( "Project %s has not been loaded. I'm a MEGA BUG! Please report me!" % projectName )
      return False
    config = self.__configs[ projectName ]
    if not config.isSection( releaseVersion ):
      gLogger.error( "Release %s is not defined for project %s" % ( releaseVersion, projectName ) )
      return False
    #Defined Modules explicitly in the release
    modules = self.__getOpt( projectName, "modules", releaseVersion )
    if modules:
      dMods = {}
      for entry in [ entry.split( ":" ) for entry in modules.split( "," ) if entry.strip() ]:
        if len( entry ) == 1:
          dMods[ entry[0].strip() ] = releaseVersion
        else:
          dMods[ entry[0].strip() ] = entry[1].strip()
      modules = dMods
    else:
      #Default modules with the same version as the release version
      modules = self.__getOpt( projectName, "defaultModules" )
      if modules:
        modules = dict( [ ( modName.strip() , releaseVersion ) for modName in modules.split( "," ) if modName.strip() ] )
      else:
        #Mod = projectName and same version
        modules = { projectName : releaseVersion }
    #Check projectName is in the modNames if not DIRAC
    if projectName != "DIRAC":
      for modName in modules:
        if modName.find( projectName ) != 0:
          gLogger.error( "Module %s does not start with the project name %s" ( modName, projectName ) )
          return Falseorigin / release - procedure
    return modules

  def getModSource( self, projectName, modName ):
    if not projectName in self.__projects:
      gLogger.fatal( "Project %s has not been loaded. I'm a MEGA BUG! Please report me!" % projectName )
      return False
    modLocation = self.__getOpt( projectName, "src_%s" % modName )
    if not modLocation:
      gLogger.error( "Source origin for module %s is not defined" % modName )
      return False
    modTpl = [ field.strip() for field in modLocation.split( "|" ) if field.strip() ]
    if len( modTpl ) == 1:
      return ( False, modTpl[0] )
    return ( modTpl[0], modTpl[1] )

  def getExtenalsVersion( self, releaseVersion ):
    if 'DIRAC' not in self.__projects:
      return False
    return self.__configs[ 'DIRAC' ].get( 'externals', releaseVersion )


class DistributionMaker:

  def __init__( self, cliParams ):
    self.cliParams = cliParams
    self.relConf = ReleaseConfig()

  def isOK( self ):
    if not self.cliParams.releasesToBuild:
      gLogger.error( "Missing releases to build!" )
      Script.showHelp()
      return False

    if self.cliParams.projectName not in projectMapping:
      gLogger.error( "Don't know how to find releases.ini for %s" % self.cliParams.projectName )
      return False

    if not self.cliParams.destination:
      self.cliParams.destination = tempfile.mkdtemp( 'DiracDist' )
    else:
      try:
        os.makedirs( self.cliParams.destination )
      except:
        pass
    gLogger.notice( "Will generate tarballs in %s" % self.cliParams.destination )
    return True

  def loadReleases( self ):
    gLogger.notice( "Loading releases.ini" )
    return self.relConf.loadProject( self.cliParams.projectName, self.cliParams.relini )

  def createModuleTarballs( self ):
    for version in self.cliParams.releasesToBuild:
      if not self.__createReleaseTarballs( version ):
        return False
    return True

  def __createReleaseTarballs( self, releaseVersion ):
    modsToTar = self.relConf.getModulesForProjectRelease( self.cliParams.projectName, releaseVersion )
    if not modsToTar:
      return False
    for modName in modsToTar:
      modVersion = modsToTar[ modName ]
      dctArgs = []
      #Version
      dctArgs.append( "-n '%s'" % modName )
      dctArgs.append( "-v '%s'" % modVersion )
      gLogger.notice( "Creating tar for %s version %s" % ( modName, modVersion ) )
      #Source
      modSrcTuple = self.relConf.getModSource( self.cliParams.projectName, modName )
      if not modSrcTuple:
        return False
      if modSrcTuple[0]:
        logMsgVCS = modSrcTuple[0]
        dctArgs.append( "-z '%s'" % modSrcTuple[0] )
      else:
        logMsgVCS = "autodiscover"
      dctArgs.append( "-u '%s'" % modSrcTuple[1] )
      gLogger.info( "Sources will be retrieved from %s (%s)" % ( modSrcTuple[1], logMsgVCS ) )
      #Tar destination
      dctArgs.append( "-D '%s'" % self.cliParams.destination )
      #Script location discovery
      scriptName = os.path.join( os.path.dirname( __file__ ), "dirac-create-distribution-tarball.py" )
      cmd = "'%s' %s" % ( scriptName, " ".join( dctArgs ) )
      gLogger.verbose( "Executing %s" % cmd )
      if os.system( cmd ):
        gLogger.error( "Failed creating tarball for module %s. Aborting" % modName )
        return False
      gLogger.info( "Tarball for %s version %s created" % ( modName, modVersion ) )
    return True


  def getAvailableExternals( self ):
    packagesURL = "http://lhcbproject.web.cern.ch/lhcbproject/dist/DIRAC3/tars/tars.list"
    try:
      remoteFile = urllib2.urlopen( packagesURL )
    except urllib2.URLError:
      gLogger.exception()
      return []
    remoteData = remoteFile.read()
    remoteFile.close()
    versionRE = re.compile( "Externals-([a-zA-Z]*)-([a-zA-Z0-9]*(?:-pre[0-9]+)*)-(.*)-(python[0-9]+)\.tar\.gz" )
    availableExternals = []
    for line in remoteData.split( "\n" ):
      res = versionRE.search( line )
      if res:
        availableExternals.append( res.groups() )
    return availableExternals

  def createExternalsTarballs( self ):
    extDone = []
    for releaseVersion in self.cliParams.releasesToBuild:
      if releaseVersion in extDone:
        continue
      if not self.tarExternals( releaseVersion ):
        return False
      extDone.append( releaseVersion )
    return True

  def tarExternals( self, releaseVersion ):
    externalsVersion = self.relConf.getExtenalsVersion( releaseVersion )
    platform = Platform.getPlatformString()
    availableExternals = self.getAvailableExternals()


    if not externalsVersion:
      gLogger.notice( "Externals is not defined for release %s" % releaseVersion )
      return False

    for externalType in self.cliParams.externalsBuildType:
      requestedExternals = ( externalType, externalsVersion, platform, 'python%s' % self.cliParams.externalsPython )
      requestedExternalsString = "-".join( list( requestedExternals ) )
      gLogger.notice( "Trying to compile %s externals..." % requestedExternalsString )
      if not self.cliParams.forceExternals and requestedExternals in availableExternals:
        gLogger.notice( "Externals %s is already compiled, skipping..." % ( requestedExternalsString ) )
        continue
      compileScript = os.path.join( os.path.dirname( __file__ ), "dirac-compile-externals" )
      if not os.path.isfile( compileScript ):
        compileScript = os.path.join( os.path.dirname( __file__ ), "dirac-compile-externals.py" )
      compileTarget = os.path.join( self.cliParams.destination, platform )
      cmdArgs = []
      cmdArgs.append( "-D '%s'" % compileTarget )
      cmdArgs.append( "-t '%s'" % externalType )
      cmdArgs.append( "-v '%s'" % externalsVersion )
      cmdArgs.append( "-i '%s'" % self.cliParams.externalsPython )
      if cliParams.externalsLocation:
        cmdArgs.append( "-e '%s'" % self.cliParams.externalsLocation )
      if cliParams.makeJobs:
        cmdArgs.append( "-j '%s'" % self.cliParams.makeJobs )
      compileCmd = "%s %s" % ( compileScript, " ".join( cmdArgs ) )
      gLogger.info( compileCmd )
      if os.system( compileCmd ):
        gLogger.error( "Error while compiling externals!" )
        sys.exit( 1 )
      tarfilePath = os.path.join( self.cliParams.destination, "Externals-%s.tar.gz" % ( requestedExternalsString ) )
      result = Distribution.createTarball( tarfilePath,
                                           compileTarget,
                                           os.path.join( self.cliParams.destination, "mysql" ) )
      if not result[ 'OK' ]:
        gLogger.error( "Could not generate tarball for package %s" % package, result[ 'Error' ] )
        sys.exit( 1 )
      os.system( "rm -rf '%s'" % compileTarget )

  def doTheMagic( self ):
    if not distMaker.isOK():
      gLogger.fatal( "There was an error with the release description" )
      return False
    if not distMaker.loadReleases():
      gLogger.fatal( "There was an error when loading the release.ini file" )
      return False
    #Module tars
    if self.cliParams.ignorePackages:
      gLogger.notice( "Skipping creating module tarballs" )
    else:
      if not self.createModuleTarballs():
        gLogger.fatal( "There was a problem when creating the module tarballs" )
        return False
    #Externals
    if self.cliParams.ignoreExternals:
      gLogger.notice( "Skipping creating externals tarball" )
    else:
      if not self.createExternalsTarballs():
        gLogger.fatal( "There was a problem when creating the Externals tarballs" )
        return False
    #Write the releases files
    reliniData = self.relConf.getConf( self.cliParams.projectName ).toString()
    for relVersion in self.cliParams.releasesToBuild:
      try:
        relFile = file( os.path.join( self.cliParams.destination, "releases-%s-%s.ini" % self.cliParams.projectName, relVersion ), "w" )
        relFile.write( reliniData )
        relFile.close()
      except Excetion, exc:
        gLogger.fatal( "Could not write the release info: %s" % str( exc ) )
        return False
    return True

if __name__ == "__main__":
  cliParams = Params()
  Script.disableCS()
  Script.addDefaultOptionValue( "/DIRAC/Setup", "Dummy" )
  cliParams.registerSwitches()
  Script.parseCommandLine( ignoreErrors = False )
  distMaker = DistributionMaker( cliParams )
  if not distMaker.doTheMagic():
    sys.exit( 1 )
  gLogger.notice( "Everything seems ok. Tarballs generated in %s" % cliParams.destination )
  if cliParams.projectName in ( "DIRAC", "LHCb" ):
    gLogger.notice( "( cd %s ; tar -cf - *.tar.gz *.md5 *.ini ) | ssh lhcbprod@lxplus.cern.ch 'cd /afs/cern.ch/lhcb/distribution/DIRAC3/tars &&  tar -xvf - && ls *.tar.gz > tars.list'" % cliParams.destination )
