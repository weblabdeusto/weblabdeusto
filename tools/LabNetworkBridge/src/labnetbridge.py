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
    if cfg.get("bridges") is None:
        raise Exception("Config does not seem to have any 'bridge'")

    # Check that there is at least one location
    if len(cfg["bridges"]) == 0:
        raise Exception("Config does not seem to have locations")

    for location_name, location in cfg["bridges"].items():
        if location.get("proto") is None:
            raise Exception("Location {0} seems to not have a 'proto' node".format(location))
        if location.get("experiments") is None:
            raise Exception("Location {0} seems to not have an 'experiments' node".format(location))

        for experiment_name, experiment in location.get("experiments").items():
            if experiment.get("listen") is None:
                raise Exception("Experiment {0} seems to not have a 'listen' node".format(experiment))

    # TODO: More checks