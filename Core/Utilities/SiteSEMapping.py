'''  The SiteSEMapping module performs the necessary CS gymnastics to
     resolve site and SE combinations.  These manipulations are necessary
     in several components.
'''

from DIRAC import gConfig, gLogger, S_OK, S_ERROR
from DIRAC.ConfigurationSystem.Client.Helpers.Path        import cfgPath
from DIRAC.ConfigurationSystem.Client.Helpers.Operations  import Operations
from DIRAC.ConfigurationSystem.Client.Helpers.Resources   import Resources, getResourceDomains, getSites, getSiteDomains

def getSiteSEMapping( gridDomainsSelected = [] ):
  ''' Returns a dictionary of all sites and their localSEs as a list, e.g.
      {'LCG.CERN.ch':['CERN-RAW','CERN-RDST',...]}
      If gridDomains is specified, result is restricted to those Grid domains.
  '''
  siteSEMapping = {}
  
  #get the sites list
  sites = getSites()
  if not sites['OK']:
    gLogger.warn( 'Problem retrieving the list of sites' )
    return sites
  else:
    sites = sites['Value']

  #getting the domains list
  gridDomains = getResourceDomains()
  if not gridDomains['OK']:
    gLogger.warn( 'Problem retrieving grid domains' )
    return gridDomains
  else:
    gridDomains = gridDomains['Value']
  
  # discriminating on the domains list
  gridDomains = list(set(gridDomains) - set(gridDomainsSelected))

  gLogger.debug( 'Grid Domains are: %s' % ( ', '.join( gridDomains ) ) )
  
  #getting only those sites pertaining to the selected domains
  sitesList = list( sites )
  for site in sites:
    siteDomains = getSiteDomains( site )
    if not siteDomains['OK']:
      return siteDomains
    else:
      if not set( siteDomains ) & set( gridDomains ):
        sitesList.remove( site )

  for site in sitesList:
    res = Resources().getStorageElements( site )
    if not res['OK']:
      gLogger.debug( res['Message'] )
    else:
      siteSEMapping[site] = res['Value']

  # Add Sites from the SiteLocalSEMapping in the CS
  cfgLocalSEPath = cfgPath( 'SiteLocalSEMapping' )
  opsHelper = Operations()
  result = opsHelper.getOptionsDict( cfgLocalSEPath )
  if result['OK']:
    mapping = result['Value']
    for site in mapping:
      ses = opsHelper.getValue( cfgPath( cfgLocalSEPath, site ), [] )
      if not ses:
        continue
      if gridDomainsSelected and site not in sitesList:
        continue
      if site not in siteSEMapping:
        siteSEMapping[site] = []
      for se in ses:
        if se not in siteSEMapping[site]:
          siteSEMapping[site].append( se )

  return S_OK( siteSEMapping )

def getSESiteMapping( gridName = '' ):
  ''' Returns a dictionary of all SEs and their associated site(s), e.g.
      {'CERN-RAW':'LCG.CERN.ch','CERN-RDST':'LCG.CERN.ch',...]}
      Although normally one site exists for a given SE, it is possible over all
      Grid types to have multiple entries.
      If gridName is specified, result is restricted to that Grid type.
      Assumes CS structure of: /Resources/Sites/<GRIDNAME>/<SITENAME>
  '''
  seSiteMapping = {}
  gridDomains = gConfig.getSections( '/Resources/Sites/' )
  if not gridDomains['OK']:
    gLogger.warn( 'Problem retrieving sections in /Resources/Sites' )
    return gridDomains

  gridDomains = gridDomains['Value']
  if gridName:
    if not gridName in gridDomains:
      return S_ERROR( 'Could not get sections for /Resources/Sites/%s' % gridName )
    gridDomains = [gridName]

  gLogger.debug( 'Grid Types are: %s' % ( ', '.join( gridDomains ) ) )
  for grid in gridDomains:
    sites = gConfig.getSections( '/Resources/Sites/%s' % grid )
    if not sites['OK']: #gConfig returns S_ERROR for empty sections until version
      gLogger.warn( 'Problem retrieving /Resources/Sites/%s section' % grid )
      return sites
    if sites:
      for candidate in sites['Value']:
        siteSEs = gConfig.getValue( '/Resources/Sites/%s/%s/SE' % ( grid, candidate ), [] )
        for se in siteSEs:
          if se not in seSiteMapping:
            seSiteMapping[se] = []
          seSiteMapping[se].append( candidate )

  return S_OK( seSiteMapping )

#############################################################################
def getSitesForSE( storageElement, gridName = '' ):
  ''' Given a DIRAC SE name this method returns a list of corresponding sites.
      Optionally restrict to Grid specified by name.
  '''

  result = getSiteSEMapping( gridName )
  if not result['OK']:
    return result

  mapping = result['Value']

  finalSites = []

  for site in mapping:
    if storageElement in mapping[site]:
      finalSites.append( site )
  return S_OK( finalSites )


#############################################################################
def getSEsForSite( siteName ):
  ''' Given a DIRAC site name this method returns a list of corresponding SEs.
  '''
  result = getSiteSEMapping()
  if not result['OK']:
    return result

  mapping = result['Value']
  if siteName in mapping:
    return S_OK( mapping[siteName] )

  return S_OK( [] )

#############################################################################
def isSameSiteSE( se1, se2 ):
  ''' Check if the 2 SEs are from the same site
  '''
  if se1 == se2:
    return S_OK( True )

  result = getSitesForSE( se1 )
  if not result['OK']:
    return result
  sites1 = result['Value']
  result = getSitesForSE( se2 )
  if not result['OK']:
    return result
  sites2 = result['Value']

  for site in sites1:
    if site in sites2:
      return S_OK( True )

  return S_OK( False )

#############################################################################
def getSEsForCountry( country ):
  ''' Determines the associated SEs from the country code
  '''
  mappedCountries = [country]
  while True:
    mappedCountry = gConfig.getValue( '/Resources/Countries/%s/AssignedTo' % country, country )
    if mappedCountry == country:
      break
    elif mappedCountry in mappedCountries:
      return S_ERROR( 'Circular mapping detected for %s' % country )
    else:
      country = mappedCountry
      mappedCountries.append( mappedCountry )
  res = gConfig.getOptionsDict( '/Resources/Countries/%s/AssociatedSEs' % country )
  if not res['OK']:
    return S_ERROR( 'Failed to obtain AssociatedSEs for %s' % country )
  return S_OK( res['Value'].values() )
