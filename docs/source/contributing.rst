.. _contributing:

Contribute
==========

.. contents:: Table of Contents

Introduction
------------

This section is focused on enabling external people to contribute the project.
WebLab-Deusto is an Open Source and non for profit project. Help us to improve
the system. You do not need to be a software developer to contribute!

Documentation
-------------

Documentation is not as maintained as we would like. If you find something that could be better described in a different way, feel free to go to our `github doc repository <https://github.com/weblabdeusto/weblabdeusto/tree/master/docs/source>`_, click on any file, and then on edit (given a file, search for "History" and next to it you'll find the Edit button). You will need to create a github account first and be logged in with that account. Once you do it and save changes, we are notified and can apply the changes (but it will be clearly acknowledged in github that you're the person doing the change).


Translations
------------

Translations are very welcome, and nowadays it's pretty simple to contribute a translation. In the `github repository <http://github.com/weblabdeusto/weblabdeusto/>`_, you may go to the::

  client/src/es/deusto/weblab/client/i18n

directory and find a file called ``IWebLabI18N.properties``. If you're in github, click on ``Raw`` to see the file and you can save it. Make sure that the extension of the file is ``.properties`` when you download it (and not ``.txt``). This is very important in Microsoft Windows, where certain browsers will change the extension calling it ``.properties.txt``: if you double click the file and it opens it with the text editor automatically, you should change the extension. The other approach is to download the whole repository (you may have done it before) as detailed in :ref:`sec-download-git`. Then, the file is located in the directory explained above, with the proper ``.properties`` extension.

Once you have the file, you may use the `Google Translator Toolkit <http://translate.google.com/toolkit/>`_. You should take the file, open it, replace all the *''* by *'*. Then, you should go to the `Google Translator Toolkit <http://translate.google.com/toolkit/>`_ and upload the file. You will be able to select the original language (english) and the target language (the one you want to translate it to). Then, it will show you an interactive environment where Google has tried to translate most of the sentences. Many of them will be wrong, but it is much easier to correct the file than to start from scratch. Furthermore, the tool is collaborative, so you may add other translators and split the sentences among them.

Then, please submit the file to the WebLab-Deusto developers (:ref:`contact`) to incorporate it to the project.


Issue reporting
---------------

WebLab-Deusto has bugs (it may work wrong in certain circumstances), as well as many things to improve in many ways. If you find a bug, or if you think of particular things that should be changed (e.g., *I miss a documentation page for this*, *this tool is not generating what I expect here*, *I would like to be able to do this*), please, tell us, we are eager to hear you.

You may do this in public by reporting an issue in our issue tracker, which is `in github <https://github.com/weblabdeusto/weblabdeusto/issues/>`_. Or if you prefer doing this in private, just :ref:`contact us <contact>`.


Bug fixes
---------

If you find a bug, and you think you can fix it, you can do three things:

* Just publish it in the public mailing list or notify the developers (:ref:`contact`).

* Create an account in `github <http://github.com/>`, fork `the project <http://github.com/weblabdeusto/weblabdeusto/>`_ by clicking on ``Fork``, and in your copy of the project, modify whatever you need. Then, create a pull request through github. We will be notified, review the code and apply the changes.

New functionalities
-------------------

If you want to create a new functionality not present in WebLab-Deusto, you are very welcome. Feel free to discuss it with us in the mailing lists, or do a prototype. Also, refer to the :ref:`weblabdeusto_development` section.

Add remote laboratories to the network
--------------------------------------

You have made a super cool remote lab using WebLab-Deusto? Please, :ref:`contact us <contact>` to do any (or all) of the following:

* Add the code to the WebLab-Deusto repository. We will make sure that if we change anything, the laboratory is still compliant.
* Advertise it in the documents.
* Share it with other universities and schools.
* Add it to the demo account in the main WebLab-Deusto repository.
* Add it to the default account created when you create a new WebLab-Deusto repository.

