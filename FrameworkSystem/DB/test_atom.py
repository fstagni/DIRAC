""" Tests DB vs Service vs Client access
"""

import concurrent.futures

from DIRAC.Core.Base.Script import parseCommandLine
parseCommandLine()

from DIRAC.FrameworkSystem.DB.AtomDB import AtomDB
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.FrameworkSystem.Client.AtomClient import AtomClient

db = AtomDB()
rpc = RPCClient("Framework/Atom")
client = AtomClient()

def testDB_reinit():
  db_o = AtomDB()
  db_o.put("bof")
  db_o.get("bof")
  db_o.remove("bof")


def testDB():
  db.put("bof")
  db.get("bof")
  db.remove("bof")


def testRPC():
  rpc.put("bah")
  rpc.get("bah")
  rpc.remove("bah")

def testClient():
  client.put("bah")
  client.get("bah")
  client.remove("bah")



#### With a pool of AtomDBs


def testDBPool(dbp):
  dbp.put("bof")
  dbp.get("bof")
  dbp.remove("bof")

dbPool = [AtomDB()]# * 10


def testDBPoolFutures():

  with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    futuresSetDBPool = {executor.submit(testDBPool, dbp): dbp for dbp in dbPool}
    for future in concurrent.futures.as_completed(futuresSetDBPool):
      try:
        x = futuresSetDBPool[future]
      except KeyError:
        break
      try:
        _ = future.result()
      except Exception as exc:
        print '%r generated an exception: %s' % (x, exc)
      else:
        pass




#### With a pool of Atom Services


def testRPCPool(rpcp):
  rpcp.put("bof")
  rpcp.get("bof")
  rpcp.remove("bof")

rpcPool = [RPCClient("Framework/Atom")] * 10


def testRPCPoolFutures():

  with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    futuresSetRPCPool = {executor.submit(testRPCPool, rpcp): rpcp for rpcp in rpcPool}
    for future in concurrent.futures.as_completed(futuresSetRPCPool):
      try:
        x = futuresSetRPCPool[future]
      except KeyError:
        break
      try:
        _ = future.result()
      except Exception as exc:
        print '%r generated an exception: %s' % (x, exc)
      else:
        pass



#### With a pool of clienrs


def testClientPool(clientp):
  clientp.put("bof")
  clientp.get("bof")
  clientp.remove("bof")

clientPool = [AtomClient()]


def testClientPoolFutures():

  with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    futuresSetClientPool = {executor.submit(testClientPool, clientp): clientp for clientp in clientPool}
    for future in concurrent.futures.as_completed(futuresSetClientPool):
      try:
        x = futuresSetClientPool[future]
      except KeyError:
        break
      try:
        _ = future.result()
      except Exception as exc:
        print '%r generated an exception: %s' % (x, exc)
      else:
        pass



