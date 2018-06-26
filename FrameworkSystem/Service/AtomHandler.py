""" just for test
"""

__RCSID__ = 'boh'

from DIRAC import S_OK

from DIRAC.Core.DISET.RequestHandler import RequestHandler
from DIRAC.FrameworkSystem.DB.AtomDB import AtomDB


def initializeAtomHandler(serviceInfo):
  global database
  database = AtomDB()
  return S_OK()


class AtomHandler( RequestHandler ):

  types_put = [basestring]
  def export_put( self, something ):
    return S_OK(database.put(something))

  types_get = [basestring]
  def export_get( self, something ):
    return S_OK(database.get(something))

  types_remove = [basestring]
  def export_remove( self, something ):
    return S_OK(database.remove(something))
