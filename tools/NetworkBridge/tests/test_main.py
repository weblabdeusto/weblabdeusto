
import labnetbridge


def test_parse_config():
    cfg = labnetbridge.parse_config("data/config.test.yml")
    assert cfg is not None
    assert cfg["bridges"] is not None

    labnetbridge.verify_config(cfg)
