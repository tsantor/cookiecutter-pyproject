from {{cookiecutter.package_dir}}.utils import get_mac_address


def test_get_mac_address():
    mac = get_mac_address()
    assert isinstance(mac, str)
