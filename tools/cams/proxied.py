from PIL import Image
import StringIO
import threading
import urllib2
import time
import requests

# Lock to protect the cache for write access.
_global_lock = threading.Lock()

# The cache.
_cache = {
    # url : [contents, lock, last_timestamp]
}

MAX_TIME = 0.1  # ms


def webcam_cache(webcam_func):
    def _webcam_caller(req, url, *args):
        return _wrapper_webcam(req, url, webcam_func, *args)

    return _webcam_caller


@webcam_cache
def _webcam(req, url):
    req.content_type = "image/jpg"
    req.headers_out["Cache-Control"] = "no-cache"
    req.headers_out["Pragma-directive"] = "no-cache"
    req.headers_out["Cache-directive"] = "no-cache"
    req.headers_out["Pragma"] = "no-cache"
    req.headers_out["Expires"] = "0"

    try:
        content = requests.get(url).content
    except:
        content = "ERROR"
        req.content_type = "text"
    return content

@webcam_cache
def _webcam_rotate(req, url, degrees = 90):
    req.content_type = "image/jpg"
    req.headers_out["Cache-Control"] = "no-cache"
    req.headers_out["Pragma-directive"] = "no-cache"
    req.headers_out["Cache-directive"] = "no-cache"
    req.headers_out["Pragma"] = "no-cache"
    req.headers_out["Expires"] = "0"

    # return str(degrees)

    try:
        sio_in = StringIO.StringIO(urllib2.urlopen(url).read())
        img = Image.open(sio_in)
        img2 = img.rotate(degrees)
        sio_out = StringIO.StringIO()
        img2.save(sio_out, 'jpeg')
        content = sio_out.getvalue()
    except:
        req.content_type = "text"
        content = "ERROR"
    return content


@webcam_cache
def _webcam_external(req, url):
    req.content_type = "image/jpg"
    req.headers_out["Cache-Control"] = "no-cache"
    req.headers_out["Pragma-directive"] = "no-cache"
    req.headers_out["Cache-directive"] = "no-cache"
    req.headers_out["Pragma"] = "no-cache"
    req.headers_out["Expires"] = "0"

    # proxy = urllib2.ProxyHandler({'http': ''})
    proxy = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy)
    try:
        content = opener.open(url).read()
    except:
        content = "ERROR"
        req.content_type = "text"
    return content


def _wrapper_webcam(req, url, webcam_func, *args):
    req.content_type = "image/jpg"
    req.headers_out["Cache-Control"] = "no-cache"
    req.headers_out["Pragma-directive"] = "no-cache"
    req.headers_out["Cache-directive"] = "no-cache"
    req.headers_out["Pragma"] = "no-cache"
    req.headers_out["Expires"] = "0"

    # Check whether our URL is in the cache
    if url not in _cache:
        # We are going to add the entry, we lock globally.
        with _global_lock:
            if url not in _cache:
                contents = webcam_func(req, url, *args)  # Problem: _fake_webcam is the slow func.
                _cache[url] = [contents, threading.Lock(), time.time()]
                return contents

    # Our cache entry does exist. We access it directly. We don't really mind
    # if we access the previous value because of threading issues.
    cache_entry = _cache[url]
    contents, lock, last_timestamp = cache_entry
    elapsed = time.time() - last_timestamp
    if elapsed > MAX_TIME:
        # Our entry has expired. We need to update it. We'll only lock our entry.
        with lock:
            if time.time() - last_timestamp > MAX_TIME:
                contents = webcam_func(req, url, *args)
                cache_entry[0] = contents
                last_timestamp = time.time()
                cache_entry[2] = last_timestamp
    return contents


def fpga1(req, *args, **kwargs):
    return _webcam_rotate(req, "http://192.168.3.72/image.jpg", 180)


def pld1(req, *args, **kwargs):
    return _webcam(req, "http://192.168.0.62/cgi-bin/video.jpg")


def pld2(req, *args, **kwargs):
    return _webcam(req, "http://192.168.0.64/cgi-bin/video.jpg?size=2")


def robot2(req, *args, **kwargs):
    return _webcam(req, "http://192.168.0.81/img/snapshot.cgi?size=2")


