#!/usr/bin/python

import requests
import time

program = """
#include <stdio.h>

int main(void)
{
}
"""

def test():
    resp = requests.post("http://localhost/weblab/web/compiserv/queue/armc", files={"main.c": ("main.c", program, "text/plain")})
    resp = resp.json()

    uid = resp["uid"]

    assert resp["result"] == "accepted"


    time.sleep(10)

    resp = requests.get("http://localhost/weblab/web/compiserv/queue/armc/{0}".format(uid))
    resp = resp.json()
    print resp

    time.sleep(10)

    resp = requests.get("http://localhost/weblab/web/compiserv/queue/armc/{0}".format(uid))
    resp = resp.json()
    print resp

    time.sleep(10)

    resp = requests.get("http://localhost/weblab/web/compiserv/queue/armc/{0}".format(uid))
    resp = resp.json()
    print resp


test()


