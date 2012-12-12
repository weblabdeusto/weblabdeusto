.. _external_tools_federation:

External tools integration through federation
=============================================

The easiest way to make it work from external tools is using the federation API.
We currently provide APIs for various programming languages (`.NET
<https://github.com/weblabdeusto/weblabdeusto/tree/master/server/consumers/dotnet>`_,
`PHP
<https://github.com/weblabdeusto/weblabdeusto/tree/master/server/consumers/php>`_, `Python <https://github.com/weblabdeusto/weblabdeusto/blob/master/server/src/weblab/core/coordinator/clients/weblabdeusto.py>`_),
and there are external efforts for other languages (`Ruby
<https://github.com/lms4labs/deustorb>`_).

As described in the :ref:`federation section <federation>`, WebLab-Deusto
supports federation. This means that two WebLab-Deusto systems can exchange
remote labs without dealing with particular users, as seen in the following
figure:

.. image:: /_static/federation_external_step1.png
   :width: 700 px
   :align: center

This basically means that in the example, the system deployed in ``University
A`` manages authentication and authorization, so its the one who knows who are
the users, etc. The contract between the systems of ``University A`` and
``University B`` does not need to deal with users or groups: if ``University A``
can access three different laboratories, then it's ``University A`` who must
choose which users can access each of these laboratories.

However, this idea is essentially what is aimed when integrating a remote
laboratory in a Learning or Content Management System (LMS/CMS). It is the LMS
the one that chooses what authentication mechanisms must be used, what students
are in which courses, and which courses should use which laboratories.

Therefore, using the federation APIs enable this second scheme, where the
LMS/CMS is basically a WebLab-Deusto consumer, and uses the same federation
protocol that other LMS/CMS use:

.. image:: /_static/federation_external_step2.png
   :width: 700 px
   :align: center

If the federation protocol does not support transitivity (this is, a consumer
may not re-share the laboratories to a third-party consumer), the LMS/CMS would
need to be configured with each external remote laboratory, which is not an
ideal situation. Typically, remote laboratory managers are the ones who deal
with this type of contracts. However, WebLab-Deusto supports transitivity (see
the :ref:`federation section <federation>`), so it is possible to have a local
WebLab-Deusto instance, configure it in the LMS, and configure in this
WebLab-Deusto instance as many external federated instances as required.

.. image:: /_static/federation_external_step3.png
   :width: 700 px
   :align: center

