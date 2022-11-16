.. _httpsServices:

===================================
Install HTTPS Services with Tornado
===================================

.. contents::


Background
**********

For many years, DIRAC services have been exposed through the DIPs (DISET) protocol.
Few years ago DIRAC developers started exposing DIRAC services using the HTTPs protocol.
This page explains how to migrate existing DIPs protocol to HTTPs. For a developer view, refer to :ref:`httpsTornado`.

For a summary presentation you can check `this <https://indico.cern.ch/event/852597/contributions/4331720/attachments/2241040/3799728/HttpsInDIRAC.pdf>`_.

NB: not all DIPs services can be exposed through HTTPs. For a comprehensve list, please refer to :ref:`scalingLimitations`.


How to migrate a DIPs service to using HTTPs
********************************************

This procedure is valid for all services with the exclusion of the Master Configuration Server
(for which you can find more information in the next subsection).

First, the following configuration subsections have to be added to CS::

  # "Main" section
  DIRAC
  {
    Setups
    {
      ...
      Tornado = Production
    }
  }

  # Add Tornado to Systems section
  Systems
  {
    ...
    Tornado
    {
      Production
      {
        Port = 443
      }
    }
  }


The example the follows is for the "DIRAC File Catalog" (DFC) service. This would normally be in CS as::

  Systems
  {
    ...
    DataManagement
    {
      Production
      {
        URLs
        {
          ...
          FileCatalog = dips://my.server.org:9197/DataManagement/FileCatalog
        }
        Services
        {
          ...
          FileCatalog
          {
            ...
            Port = 9197
            Protocol = dips
            ...
          }
        }
        ...
      }
    }
  }


And you need to change it to::

  Systems
  {
    ...
    DataManagement
    {
      Production
      {
        URLs
        {
          ...
          FileCatalog = https://my.server.org:8443/DataManagement/FileCatalog
        }
        Services
        {
          ...
          FileCatalog
          {
            ...
            Protocol = https
            HandlerPath = DIRAC/DataManagementSystem/Service/TornadoFileCatalogHandler.py
            ...
          }
        }
        ...
      }
    }
  }


MasterCS special case
*********************

The master CS is different because it uses the same global variable (``gConfig``) but uses it also to write config. Because of that, it needs to run in a separate process. In order to do so:

* Do NOT specify ``Protocol=https`` in the service description, otherwise it will be ran with all the other Tornado services
* If you run on the same machine as other TornadoService, specify a ``Port`` in the service description

Finally, there is no automatic installations script. So just install a CS as you normally would do, and then edit the ``run`` file like that::

  diff --git a/run b/run.new
  index d45dce1..f5f3b55 100755
  --- a/run
  +++ b/run.new
  @@ -7,6 +7,6 @@
    [ "service" = "agent" ] && renice 20 -p $$
    #
    #
  -  exec python $DIRAC/DIRAC/Core/scripts/dirac-service.py Configuration/Server --cfg /opt/dirac/pro/etc/Configuration_Server.cfg < /dev/null
  +  export DIRAC_USE_TORNADO_IOLOOP=Yes
  +  exec tornado-start-CS -ddd
