.. _federation:

Federation
==========

WebLab-Deusto natively supports federating remote laboratories. This means that
if two universities install WebLab-Deusto, any of the systems will be able to 
consume laboratories provided by the other university.

.. image:: /_static/federation.png
   :width: 500 px
   :align: center

.. contents:: Table of Contents

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

Finally, you can also `see the federation video <http://www.youtube.com/watch?v=TMdSYlFErX0>`_.

Features
--------

Two main features are provided by WebLab-Deusto: 

Transitivity
^^^^^^^^^^^^

If you're a provider of a laboratory, your consumers may technically re-share this laboratory. Basically, this enables subcontracting laboratories. `See the transitive federation video <http://www.youtube.com/watch?v=tRMwoliXy5Q>`_.

.. image:: /_static/transitivity.png
   :width: 500 px
   :align: center

Federated load balance
^^^^^^^^^^^^^^^^^^^^^^

If there are multiple providers of a copy of a laboratory, you can balance the load of users among them automatically.

.. image:: /_static/federated_load_balance.png
   :width: 500 px
   :align: center

Examples
--------

Other WebLab-Deusto deployments:

* `UNED <http://www.uned.es/>`_: http://weblab.ieec.uned.es/
* `HBRS <http://fpga-vision-lab.h-brs.de/weblab/>`_: http://fpga-vision-lab.h-brs.de/weblab/ 
* `Slovenská technická univerzita <http://www.kirp.chtf.stuba.sk/>`_: http://weblab.chtf.stuba.sk/
* `UPNA <https://www.unavarra.es>`_: https://weblab.unavarra.es/
* `TU-Dortmund <https://www.zhb.tu-dortmund.de>`_: https://weblab.zhb.tu-dortmund.de
* `FH Aachen <https://www.fh-aachen.de>`_: https://weblab.fh-aachen.de
* `UGA <https://www.uga.edu>`_: https://remotelab.engr.uga.edu
* `ISEP <https://www.isep.ipp.pt>`_: https://openlabs.isep.ipp.pt/weblab/
* `UNED (Costa Rica) <https://www.uned.ac.cr/>`_:  https://labremoto.uned.ac.cr/weblab/
* `UNAD <https://www.unad.edu.co/>`_:  https://lab-remoto-etr.unad.edu.co/weblab/ 

If you wish us to host a new deployment, contact us at weblab@deusto.es.
