import pytest
import requests


def test_binder_up(binder_url):
    """
    Binder URL is up and returning sensible text
    """
    r = requests.get(binder_url)
    assert r.status_code == 200
    assert "Sign in with GitHub" in r.text


def test_hub_up(hub_url):
    """
    Hub URL is up and returning sensible result
    """
    r = requests.get(hub_url)
    assert r.status_code == 200
    assert "Sign in with GitHub" in r.text


# The proxy-patches pod can take up to 30 seconds
# to registr its route after a proxy restart
@pytest.mark.flaky(reruns=3, reruns_delay=10)
def test_hub_user_redirect(hub_url):
    """
    Requesting a hub URL for a non-running user
    """
    # This should *NOT* redirect for now
    r = requests.get(hub_url + "/user/doesntexist")
    assert r.status_code == 404
