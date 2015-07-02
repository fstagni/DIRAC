#!/usr/bin/env python

import DIRAC
import sys

print "AAAAAAAAAAAAAAAA"

from DIRAC import S_OK, S_ERROR, gConfig

from DIRAC.Core.Base import Script
Script.parseCommandLine( ignoreErrors = True )

res = gConfig.getValue( '/LocalSite/cfg', 'NOTSET' )
print res
# sys.stdout.write( 'in MyDIRACOScript', res )

# fd = open( 'myFile' )
# fd.write( res )
# fd.close()
