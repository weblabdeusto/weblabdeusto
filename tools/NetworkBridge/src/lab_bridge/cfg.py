import codecs
import yaml

def parse_config(path):
    """
    Parses the configuration yaml file into a structure. It will be used to create the right servers, which
    will locally listen for LaboratoryServer initiated connections, and which will behave as Experiment Servers (from
    the Laboratory Server's perspective).
    :return:

    :param path: Path to the configuration yml file.
    :type path: str
    """
    f = codecs.open(path)
    configdata = yaml.load(f)
    return configdata

def verify_config(cfg):
    """
    Verifies that the configuration we have loaded *seems* to be fine.
    The checks done are not necessarily thorough. Returns None if all
    is good, returns an exception otherwise.
    :param cfg: Parsed configuration, as a dictionary.
    :type cfg: dict
    :return:
    """
    # TODO
    return None