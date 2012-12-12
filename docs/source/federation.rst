Federation
==========

WebLab-Deusto natively supports federating remote laboratories. This means that
if two universities install WebLab-Deusto, any of the systems will be able to 
consume laboratories provided by the other university.

See it in action
----------------

When you run the `WebLab-Deusto demo <https://www.weblab.deusto.es/weblab/>`_,
there is a particular laboratory called *submarine*. If you run it, you'll see
that whenever it is reserved, the web page redirects you to other domain (from
www.weblab.deusto.es to fishtank.weblab.deusto.es). Internally, there are two
independent WebLab-Deusto deployments there: one is the main system at Deusto,
the other is a constrained system running in an ARM device (called IGEPv2). The
first one (in this case, the **consumer**) is telling the second one
(**provider**), "Hi, I'm 'deusto', and I want to use this laboratory that I'm 
granted for 250 seconds for a local user here called 'demo'". Later, the
consumer will be requesting the provider for the user tracking, so the
administrators of WebLab-Deusto will be able to track the 'demo' user.

Other way to test it is by :ref:`deploying WebLab-Deusto <installation>` (the
basic default installation is a straightforward process). By default, the
installation is a consumer of a federated system which is the main server of
WebLab-Deusto. By adding different users and granting them permissions to the
robots lab, and after accessing the lab with this user you'll be able to see
in the administrator panel that it has been used.

Features
--------

Two main features are provided by WebLab-Deusto: 

* Transitivity: if you're a provider of a laboratory, your consumers may
  technically re-share this laboratory.

* Federated load balance: if there are multiple providers of a copy of a
  laboratory, you can balance the load of users among them automatically.


**This section must be extended**
