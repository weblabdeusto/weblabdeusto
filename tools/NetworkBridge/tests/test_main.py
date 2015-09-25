
from common import cfg

def test_parse_config():
    conf = cfg.parse_config("data/config.test.yml")
    assert conf is not None
    assert conf["bridges"] is not None

    cfg.verify_config(conf)
