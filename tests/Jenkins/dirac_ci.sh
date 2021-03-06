#!/usr/bin/env bash
#-------------------------------------------------------------------------------
# dirac_ci
#
# Several functions used for Jenkins style jobs
# They may also work on other CI systems
#
#
# fstagni@cern.ch
# 09/12/2014
#-------------------------------------------------------------------------------

# A CI job needs:
#
# === environment variables (minimum set):
#
# DIRACBRANCH (branch of DIRAC, e.g. rel-v7r0)
#
# === optional environment variables:
#
# WORKSPACE (set by Jenkins, normally. If not there, will be $PWD)
# DEBUG (set it to whatever value to turn on debug messages)
#
# DIRAC_RELEASE (for installing a specific release)
# ALTERNATIVE_MODULES (for installing a non-released version(s), e.g. "https://github.com/$username/DIRAC.git:::DIRAC:::someBranch")
#                     (also valid for extensions)
# DIRACOSVER (a DIRACOS version, or simply "True" for installing with DIRACOS)
#
# JENKINS_SITE (site name, by default DIRAC.Jenkins.ch)
# JENKINS_CE (CE name, by default jenkins.cern.ch)
# JENKINS_QUEUE (queue name, by default jenkins-queue_not_important)
#
# === for extensions
# INSTALL_CFG_FILE environment variable:
# location of the CFG file to be used for extensions --> where at least the following options are set:
# "LocalInstalltion/Project"
# "LocalInstalltion/VirtualOrganization"
#
# === a default directory structure is created:
# ~/TestCode
# ~/ServerInstallDIR
# ~/ClientInstallDIR



# Def of environment variables:

if [ "$DEBUG" ]; then
  echo "==> Running in DEBUG mode"
  DEBUG='-ddd'
else
  echo "==> Running in non-DEBUG mode"
fi

if [ "$WORKSPACE" ]; then
  echo "==> We are in Jenkins I guess"
else
  WORKSPACE=$PWD
fi

if [ "$DIRACBRANCH" ]; then
  echo "==> Working on DIRAC branch $DIRACBRANCH"
else
  DIRACBRANCH='integration'
fi

# Creating default structure
mkdir -p $WORKSPACE/TestCode # Where the test code resides
TESTCODE=$_
mkdir -p $WORKSPACE/ServerInstallDIR # Where servers are installed
SERVERINSTALLDIR=$_
mkdir -p $WORKSPACE/ClientInstallDIR # Where clients are installed
CLIENTINSTALLDIR=$_

# Location of the CFG file to be used (this can be replaced by the extensions)
INSTALL_CFG_FILE=$TESTCODE/DIRAC/tests/Jenkins/install.cfg

# Sourcing utility file
# shellcheck source=tests/Jenkins/utilities.sh
source "$TESTCODE/DIRAC/tests/Jenkins/utilities.sh"



#...............................................................................
#
# installSite:
#
#   This function will install DIRAC using the dirac-install.py script
#     following (more or less) instructions at dirac.rtfd.org
#
#...............................................................................

function installSite(){
  echo "==> [installSite]"

  prepareForServer

  findRelease

  generateCA
  generateCertificates

  getCFGFile

  echo "==> Fixing install.cfg file"
  sed -i "s,VAR_TargetPath,$SERVERINSTALLDIR,g" "$SERVERINSTALLDIR/install.cfg"
  sed -i "s,VAR_HostDN,$(hostname --fqdn),g" "$SERVERINSTALLDIR/install.cfg"

  sed -i "s/VAR_DB_User/$DB_USER/g" "$SERVERINSTALLDIR/install.cfg"
  sed -i "s/VAR_DB_Password/$DB_PASSWORD/g" "$SERVERINSTALLDIR/install.cfg"
  sed -i "s/VAR_DB_RootUser/$DB_ROOTUSER/g" "$SERVERINSTALLDIR/install.cfg"
  sed -i "s/VAR_DB_RootPwd/$DB_ROOTPWD/g" "$SERVERINSTALLDIR/install.cfg"
  sed -i "s/VAR_DB_Host/$DB_HOST/g" "$SERVERINSTALLDIR/install.cfg"
  sed -i "s/VAR_DB_Port/$DB_PORT/g" "$SERVERINSTALLDIR/install.cfg"
  sed -i "s/VAR_NoSQLDB_Host/$NoSQLDB_HOST/g" "$SERVERINSTALLDIR/install.cfg"
  sed -i "s/VAR_NoSQLDB_Port/$NoSQLDB_PORT/g" "$SERVERINSTALLDIR/install.cfg"

  echo "==> Started installing"

  installOptions="$DEBUG "

  # If DIRACOSVER is not defined, use LcgBundle
  if [ "$DIRACOSVER" ]; then
    if [ "$DIRACOSVER" == True ]; then
      echo "Installing with DIRACOS"
      installOptions+="--dirac-os "
    else
      echo "Installing with DIRACOS $DIRACOSVER"
      installOptions+="--dirac-os --dirac-os-version=$DIRACOSVER "
    fi
  else
    echo "Installing using externals + lcgBundle"
    installOptions+="-t fullserver "
  fi

  if [ "$ALTERNATIVE_MODULES" ]; then
    echo "Installing from non-release code"
    if [[ -d "$ALTERNATIVE_MODULES" ]]; then
      installOptions+="--module=$ALTERNATIVE_MODULES:::DIRAC:::local"
    else
      installOptions+="--module=$ALTERNATIVE_MODULES"
    fi
  fi

  echo "==> Installing with options $installOptions $SERVERINSTALLDIR/install.cfg"

  if ! "$SERVERINSTALLDIR/dirac-install.py" $installOptions "$SERVERINSTALLDIR/install.cfg"; then
    echo "ERROR: dirac-install.py failed"
    exit 1
  fi

  echo "==> Done installing, now configuring"
  source "$SERVERINSTALLDIR/bashrc"
  if ! dirac-configure "$SERVERINSTALLDIR/install.cfg" "$DEBUG"; then
    echo "ERROR: dirac-configure failed"
    exit 1
  fi

  echo "=> The pilot flag should be False"
  if ! dirac-configure -o /Operations/Defaults/Pilot/UpdatePilotCStoJSONFile=False -FDMH "$DEBUG"; then
    echo "ERROR: dirac-configure failed"
    exit 1
  fi

  if ! dirac-setup-site "$DEBUG"; then
    echo "ERROR: dirac-setup-site failed"
    exit 1
  fi

  echo "==> Completed installation"

}


#...............................................................................
#
# fullInstall:
#
#   This function install all the DIRAC stuff known...
#
#...............................................................................

function fullInstallDIRAC(){
  echo "==> [fullInstallDIRAC]"

  finalCleanup

  killRunsv

  # install ElasticSearch locally
  if [[ -z $NoSQLDB_HOST || $NoSQLDB_HOST == "localhost" ]]; then
      echo "Installing ElasticSearch locally"
      installES
  else
      echo "NoSQLDB_HOST != localhost, skipping local ElasticSearch install"
  fi

  #basic install, with only the CS (and ComponentMonitoring) running, together with DB InstalledComponentsDB, which is needed)
  if ! installSite; then
    echo "ERROR: installSite failed"
    exit 1
  fi

  # Dealing with security stuff
  # generateCertificates
  if ! generateUserCredentials; then
    echo "ERROR: generateUserCredentials failed"
    exit 1
  fi

  if ! diracCredentials; then
    echo "ERROR: diracCredentials failed"
    exit 1
  fi

  #just add a site
  if ! diracAddSite; then
    echo "ERROR: diracAddSite failed"
    exit 1
  fi

  #Install the Framework
  findDatabases 'FrameworkSystem'
  dropDBs
  if ! diracDBs; then
    echo "ERROR: diracDBs failed"
    exit 1
  fi

  findServices 'FrameworkSystem'
  if ! diracServices; then
    echo "ERROR: diracServices failed"
    exit 1
  fi

  #create groups
  if ! diracUserAndGroup; then
    echo "ERROR: diracUserAndGroup failed"
    exit 1
  fi

  echo "==> Restarting Framework ProxyManager"
  dirac-restart-component Framework ProxyManager $DEBUG

  echo "==> Restarting Framework ComponentMonitoring"
  dirac-restart-component Framework ComponentMonitoring $DEBUG

  #Now all the rest

  #DBs (not looking for FrameworkSystem ones, already installed)
  findDatabases 'exclude' 'FrameworkSystem'
  dropDBs
  if ! diracDBs; then
    echo "ERROR: diracDBs failed"
    exit 1
  fi

  #upload proxies
  if ! diracProxies; then
    echo "ERROR: diracProxies failed"
    exit 1
  fi

  #fix the DBs (for the FileCatalog)
  diracDFCDB
  python "$TESTCODE/DIRAC/tests/Jenkins/dirac-cfg-update-dbs.py" "$DEBUG"

  #services (not looking for FrameworkSystem already installed)
  findServices 'exclude' 'FrameworkSystem'
  if ! diracServices; then
    echo "ERROR: diracServices failed"
    exit 1
  fi

  #fix the DFC services options
  python "$TESTCODE/DIRAC/tests/Jenkins/dirac-cfg-update-services.py" "$DEBUG"

  #fix the SandboxStore and other stuff
  python "$TESTCODE/DIRAC/tests/Jenkins/dirac-cfg-update-server.py" dirac-JenkinsSetup "$DEBUG"

  echo "==> Restarting WorkloadManagement SandboxStore"
  dirac-restart-component WorkloadManagement SandboxStore $DEBUG

  echo "==> Restarting WorkloadManagement Matcher"
  dirac-restart-component WorkloadManagement Matcher $DEBUG

  echo "==> Restarting DataManagement FileCatalog"
  dirac-restart-component DataManagement FileCatalog $DEBUG

  echo "==> Restarting Configuration Server"
  dirac-restart-component Configuration Server $DEBUG

  echo "==> Restarting ResourceStatus ResourceStatus"
  dirac-restart-component ResourceStatus ResourceStatus $DEBUG

  echo "==> Restarting ResourceStatus ResourceManagement"
  dirac-restart-component ResourceStatus ResourceManagement $DEBUG

  echo "==> Restarting ResourceStatus Publisher"
  dirac-restart-component ResourceStatus Publisher $DEBUG

  # populate RSS
  echo "==> Populating RSS DB"
  dirac-rss-sync --element Site -o LogLevel=VERBOSE
  dirac-rss-sync --element Resource -o LogLevel=VERBOSE
  # init RSS
  echo "==> Initializing status of sites and resources in RSS"
  dirac-rss-sync --init -o LogLevel=VERBOSE
  # Setting by hand
  dirac-rss-set-status --element Resource --name ProductionSandboxSE --status Active --reason "Why not?"
  dirac-rss-set-status --element Resource --name jenkins.cern.ch --status Active --reason "Why not?"
  dirac-rss-set-status --element Resource --name JENKINS-FTS3 --status Active --reason "Why not?"
  dirac-rss-set-status --element Resource --name FileCatalog --status Active --reason "Why not?"
  dirac-rss-set-status --element Site --name DIRAC.Jenkins.ch --status Active --reason "Why not?"

  #agents
  findAgents
  if ! diracAgents; then
    echo "ERROR: diracAgents failed"
    exit 1
  fi
}


#...............................................................................
#
# miniInstallDIRAC:
#
#   This function install the bare minimum of DIRAC
#
#...............................................................................

function miniInstallDIRAC(){
  echo "==> [miniInstallDIRAC]"

  finalCleanup

  killRunsv

  # basic install, with only the CS (and ComponentMonitoring) running, together with DB InstalledComponentsDB, which is needed)
  if ! installSite; then
    echo "ERROR: installSite failed"
    exit 1
  fi

  # Dealing with security stuff
  # generateCertificates
  if ! generateUserCredentials; then
    echo "ERROR: generateUserCredentials failed"
    exit 1
  fi

  if ! diracCredentials; then
    echo "ERROR: diracCredentials failed"
    exit 1
  fi

  # just add a site
  if ! diracAddSite; then
    echo "ERROR: diracAddSite failed"
    exit 1
  fi

  # fix the SandboxStore and other stuff
  python "$TESTCODE/DIRAC/tests/Jenkins/dirac-cfg-update-server.py" dirac-JenkinsSetup "$DEBUG"

  echo "==> Restarting Configuration Server"
  dirac-restart-component Configuration Server $DEBUG
}



function clean(){

  echo "==> [clean]"

  #### make sure we're using the server
  if ! cd "$SERVERINSTALLDIR"; then
    echo "ERROR: cannot change to $SERVERINSTALLDIR"
    exit 1
  fi
  if ! source bashrc; then
    echo "ERROR: cannot source bashrc"
    exit 1
  fi
  ####

  # Uninstalling the services
  diracUninstallServices

  # stopping runsv of services and agents
  stopRunsv

  # DBs
  findDatabases
  dropDBs
  mysql -u"$DB_ROOTUSER" -p"$DB_ROOTPWD" -h"$DB_HOST" -P"$DB_PORT" -e "DROP DATABASE IF EXISTS FileCatalogDB;"
  mysql -u"$DB_ROOTUSER" -p"$DB_ROOTPWD" -h"$DB_HOST" -P"$DB_PORT" -e "DROP DATABASE IF EXISTS InstalledComponentsDB;"

  killES

  # clean all
  finalCleanup
}
