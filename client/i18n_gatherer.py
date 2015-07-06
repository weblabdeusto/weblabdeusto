#!/usr/bin/env python
import re
import json
import glob
import codecs
import ConfigParser
from collections import OrderedDict

english = "src/es/deusto/weblab/client/i18n/IWebLabI18N.properties"
languages = glob.glob("src/es/deusto/weblab/client/i18n/IWebLabI18N_*.properties")

messages = OrderedDict() # {
#    lang : {
#      key : value
#    }
# }

for lang_file in sorted(languages):
    lang = lang_file.rsplit('_', 1)[1].split('.')[0]
    lang_messages = OrderedDict()
    for line in codecs.open(lang_file, encoding = 'utf-8'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue

        if '=' not in line:
            print "Wrong line: %r" % line
            continue

        key, value = line.split('=', 1)
        lang_messages[key.strip()] = value.strip()
    messages[lang] = lang_messages
    
parser = ConfigParser.ConfigParser()
parser.read(english)

translation_data = OrderedDict()
translation_data['experiments'] = OrderedDict() # {
        # 'experiment_id' : {
        #     'lang_code' : {
        #         'key' : 'value'
        #     }
        # }
    # },
translation_data['generic_experiments'] = OrderedDict() # {
        # lang_code : {
        #     key : value
        # }
    # },

translation_data['generic'] = OrderedDict() # {
        # lang_code : {
        #     key : value
        # }
    # }

for section in parser.sections():
    if section.startswith('experiment_'):
        experiment_id = section[len('experiment_'):]
        translation_data['experiments'][experiment_id] = OrderedDict()
        translation_data['experiments'][experiment_id]['en'] = OrderedDict()
        where = translation_data['experiments'][experiment_id]
    elif section == 'generic_experiments' or section == 'generic':
        translation_data[section]['en'] = OrderedDict()
        where = translation_data[section]
    else:
        print "Unknown section: %s" % section
        continue

    for key, value in parser.items(section):
        where['en'][key] = value
        for lang in messages:
            if key in messages[lang]:
                if lang not in where:
                    where[lang] = OrderedDict()
                where[lang][key] = messages[lang][key]

#########################################
# 
# 
#   "PLUG-INS" (doing some magic)
# 
# 

plugins = []

def register(plugin_class):
    plugins.append(plugin_class())

class Plugin(object):
    def get_experiment(self, client_id):
        return translation_data['experiments'][client_id]

    def add_experiment(self, client_id, data):
        translation_data['experiments'][client_id] = data

    def run(self):
        "Do something"
        

# 
# robot-movement = robot-standard = robot-proglist
# 

class Robots(Plugin):
    def run(self):
        robot_standard_translations = self.get_experiment('robot-standard')
        self.add_experiment('robot-proglist', robot_standard_translations)
        self.add_experiment('robot-movement', robot_standard_translations)

register(Robots)

# 
# archimedes
# 

class Archimedes(Plugin):
    def run(self):
        contents = ""
        catching = False
        for line in codecs.open("src/es/deusto/weblab/public/jslabs/archimedes/js/archimedes_configuration.js", encoding = 'utf-8').readlines():
            # Remove comments
            if re.match(".*//[^\"]*$", line):
                line = line.rsplit('//',1)[0]

            # if var i18n = {...
            if re.match("^\s*var\s+i18n\s*=\s*{", line):
                contents = '{' + line.split('{', 1)[1].strip()
                catching = True
            elif re.match("^.*}\s*;[^\"]*$", line):
                contents += line.rsplit(';', 1)[0].strip()
                break
            elif catching:
                contents += line.strip()

        contents = contents.strip()
        self.add_experiment("archimedes", json.JSONDecoder(object_pairs_hook=OrderedDict).decode(contents))

register(Archimedes)

# 
#

for plugin in plugins:
    plugin.run()

#########################################
# 
# 
#   File generation
#

FILE = "../server/src/weblab/i18n.json"
json.dump(translation_data, codecs.open(FILE, 'w', encoding = 'utf-8'), indent = 4)
print "%s updated" % FILE
