# $Header: /tmp/libdirac/tmp.stZoy15380/dirac/DIRAC3/DIRAC/StagerSystem/Agent/PinRequest.py,v 1.2 2009/08/07 13:15:02 acsmith Exp $
__RCSID__ = "$Id: PinRequest.py,v 1.2 2009/08/07 13:15:02 acsmith Exp $"

from DIRAC import gLogger, gConfig, gMonitor, S_OK, S_ERROR, rootPath

from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.Core.Utilities.Shifter import setupShifterProxyInEnv

from DIRAC.DataManagementSystem.Client.ReplicaManager import ReplicaManager

import time,os,sys,re
from types import *

AGENT_NAME = 'Stager/PinRequest'

class PinRequest(AgentModule):

  def initialize(self):
    self.replicaManager = ReplicaManager()
    self.stagerClient = RPCClient('dips://volhcb08.cern.ch:9149/Stager/Stager')
    self.pinLifeTime = 60*60*24*7 # 7 days
    return S_OK()

  def execute(self):
    res = setupShifterProxyInEnv('DataManager','%s/runit/%s/proxy' % (rootPath,AGENT_NAME))
    if not res['OK']:
      gLogger.fatal("PinRequest.execute: Failed to setup data manager proxy.", res['Message'])
      return res
    res = self.submitPinRequests()
    return res

  def submitPinRequests(self): 
    """ This manages the Staged->Pinned transition of the Replicas
    """
    res = self.__getStagedReplicas()
    if not res['OK']:
      gLogger.fatal("PinRequest.submitPinRequests: Failed to get replicas from StagerDB.",res['Message'])
      return res
    if not res['Value']:
      gLogger.info("PinRequest.submitPinRequests: There were no Staged replicas found")
      return res
    seReplicas = res['Value']
    for storageElement,requestIDs in seReplicas.items():
      gLogger.info("PinRequest.submitPinRequests: Obtained Staged replicas for pinning at %s." % storageElement)
      for requestID,replicas in requestIDs.items():
        self.__issuePinRequests(storageElement,requestID,replicas)
    return S_OK()

  def __getStagedReplicas(self):
    """ This obtains the Staged replicas from the Replicas table and for each LFN the requested storage element """
    # First obtain the Staged replicas from the Replicas table
    res = self.stagerClient.getStagedReplicas()
    if not res['OK']:
      gLogger.error("PinRequest.__getStagedReplicas: Failed to get replicas with Staged status.", res['Message'])
      return res
    if not res['Value']:
      gLogger.debug("PinRequest.__getStagedReplicas: No Staged replicas found to process.")
      return S_OK()
    else:
     gLogger.debug("PinRequest.__getStagedReplicas: Obtained %s Staged replicas(s) to process." % len(res['Value']))
    seReplicas = {}
    for replicaID,info in res['Value'].items():
      lfn,storageElement,size,pfn,requestID = info
      if not seReplicas.has_key(storageElement):
        seReplicas[storageElement] = {}
      if not seReplicas[storageElement].has_key(requestID):
        seReplicas[storageElement][requestID] = {}
      seReplicas[storageElement][requestID][pfn] = replicaID
    return S_OK(seReplicas)

  def __issuePinRequests(self,storageElement,requestID,replicas):
    pinRequestMetadata = {}
    # Now issue the pin requests for the remaining replicas
    if replicas:
      gLogger.info("PinRequest.submitPinRequests: Submitting %s pin requests for request %s at %s." % (len(replicas),requestID,storageElement))
      pfnsToPin = dict.fromkeys(replicas,requestID)
      res = self.replicaManager.pinPhysicalFile(pfnsToPin,storageElement,lifetime=self.pinLifeTime)
      if not res['OK']:
        gLogger.error("PinRequest.submitPinRequests: Completely failed to sumbmit pin requests for replicas.",res['Message'])
      else:
        for pfn in res['Value']['Successful'].keys():
          if not pinRequestMetadata.has_key(requestID):
            pinRequestMetadata[requestID] = []
          pinRequestMetadata[requestID].append(replicas[pfn])
    # Update the states of the replicas in the database
    if pinRequestMetadata:
      gLogger.info("PinRequest.submitPinRequest: %s pin request metadata to be updated." % len(pinRequestMetadata))
      res = self.stagerClient.insertPinRequest(pinRequestMetadata,self.pinLifeTime)
      if not res['OK']:
        gLogger.error("PinRequest.submitPinRequest: Failed to insert pin request metadata.", res['Message'])
    return
