.. _https_services:

==================================
Installing HTTPs services in DIRAC
==================================

More and more DIRAC services are available through the HTTPs protocol instead of the historical DISET (``dips://``) protocol.


General principle
=================

Contrary to the DISET protocol where each service would have its own process and port opened, HTTPs services are served by a unique process and port, based on Tornado.

There are exceptions to that, due to the use of global variables in some parts of DIRAC. Namely:

* Master CS

All other services can follow the standard procedure described below.

First of all, you should define the Tornado setup in the CS. For example::

  DIRAC/Setups/LHCb-Production/Tornado = Production



Installation of an HTTPs based service
======================================

This procedure is to be used if you are want to serve a new service with HTTPs.


Case 1: you do NOT run the equivalent DISET service
---------------------------------------------------

This is the most trivial case. Just run ``dirac-install-tornado-service`` with the service you are interested in. This will install an ``runit`` component running ``tornado-start-all``.

Case 2: you run the equivalent DISET service
--------------------------------------------

Because the CS already contains the handler definition for DISET, ``dirac-install-tornado-service`` will not modify it. Thus, you have to update it yourself, before running the command, otherwise ``tornado-start-all`` will not find any service to run, and the installation will be shown as failed.

Procedure:

#. Update by hand the CS of the desired service:

  * Remove the port definition
  * Modify the handler to point to the Tornado handler
  * add ``Protocol=https``

#. Run ``dirac-install-tornado-service`` or restart the tornado component if already running.

.. note::
  This means that from now on, the DISET service cannot be restarted anymore, as its configuration would be wrong.

Example of configuration before/after:

.. literalinclude:: /../../src/DIRAC/WorkloadManagementSystem/ConfigTemplate.cfg
   :start-after: ##BEGIN JobMonitoring
   :end-before: ##END
   :dedent: 2
   :caption: JobMonitoring configuration for DISET

.. literalinclude:: /../../src/DIRAC/WorkloadManagementSystem/ConfigTemplate.cfg
   :start-after: ##BEGIN TornadoJobMonitoring
   :end-before: ##END
   :dedent: 2
   :caption: JobMonitoring configuration for HTTPs

In any case, do not forget to update the URL of the service you just installed, such that other services can reach it.


Adding more tornado instances on a different machine
====================================================

Simply use ``dirac-install-tornado-service`` with no arguments on the new machine.
