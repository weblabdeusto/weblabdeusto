from __future__ import print_function, unicode_literals

import os
import hashlib
import datetime
import traceback

import babel
from flask import request, render_template, Response

from weblab.core.wl import weblab_api
from weblab.util import data_filename

PER_LANG = {
    # lang : {
        # 'etag' : etag string,
        # 'content' : string_contents
        # 'last_modified' : datetime.datetime
    # }
}

@weblab_api.route_webclient('/locales.json')
def locales():
    lang = request.args.get('lang')
    if not lang:
        # Default language is English
        lang = 'en'

    try:
        babel.Locale.parse(lang)
    except (babel.core.UnknownLocaleError, ValueError) as e:
        # Avoid storing fake languages
        return "Invalid language", 400

    lang_contents = PER_LANG.get(lang)

    if lang_contents is None:
        # 
        # If the language has not been previously calculated, it is calculated as follows:
        # - first, check the modified date of the locales.json and messages.mo file
        # - then, generate the file using render_template
        # - store it in the local cache, and then check the etag and so on
        # 
        fname = data_filename('weblab/core/templates/webclient/locales.json')
        try:
            modification_time = os.stat(fname).st_mtime
            last_modified = datetime.datetime.fromtimestamp(modification_time)
        except Exception as e:
            print("Could not calculate the time for %s" % fname)
            traceback.print_exc()
            last_modified = datetime.datetime.now()

        messages_directory = data_filename('weblab/core/translations')
        messages_file = data_filename('weblab/core/translations/{0}/LC_MESSAGES/messages.mo'.format(lang))
        if os.path.exists(messages_file):
            try:
                messages_modification_time = os.stat(fname).st_mtime
                messages_last_modified = datetime.datetime.fromtimestamp(messages_modification_time)
            except Exception as e:
                messages_last_modified = datetime.datetime.now()

            last_modified = max(last_modified, messages_last_modified)
            
        def ng_gettext(text):
            """Wrapper of gettext. It uses the messages_file to load particular translations (e.g. if 'es' is requested, it uses the translations for Spanish)."""
            translation = babel.support.Translations.load(messages_directory, lang)
            translated_text = translation.gettext(text)
            return translated_text

        contents = render_template('webclient/locales.json', ng_gettext=ng_gettext)
        etag = hashlib.new('sha1', contents).hexdigest()
        
        lang_contents = {
            'last_modified' : last_modified.replace(microsecond=0),
            'contents' : contents,
            'etag' : etag,
        }

        PER_LANG[lang] = lang_contents
    
    # At this point, lang_contents exists, and contains:
    #    last_modified: pointing at the latest point where the contents where modified
    #    contents: the string with the processed contents
    #    etag: with the hash of the contents
    
    # First we check etag (and return 304 if the contents were not changed)
    if request.if_none_match is not None and request.if_none_match.contains(lang_contents['etag']):
        return Response(status=304)

    # Then the date (and return 304 if the date is correct)
    if request.if_modified_since is not None and request.if_modified_since >= lang_contents['last_modified']:
        return Response(status=304)
    
    # Otherwise, we create the response
    response = Response(lang_contents['contents'])
    response.mimetype = 'application/json'
    response.last_modified = lang_contents['last_modified']
    response.set_etag(lang_contents['etag'])
    return response

