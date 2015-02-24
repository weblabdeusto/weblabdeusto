retry on error
==============

[work in progress] Wrap an async function with retry logic.

install
-------

```bash
$ npm install retry-on-error
```

usage
-----

```javascript

var retry = require('retry-on-error');
```

retry(options)

- *timeout* -- a number representing the time in ms to wait between retrys or
  a function that accepts the attempt number as its only parameter and
  returns the time in ms to wait after that attempt number. Numbers are
  use for static timeouts, and functions can be used for custom backoff
  strategies.  This module also includes functions to create common
  backoff strategies. See backoff strategy section below.
- *accept* -- predicate function that takes the same arguments
  as the callback, and returns truthy if the execution should be
  accepted as success and falsey if the execution should be
  considered a failure/error. The default accept function follows the node
  callback pattern where the first parameter to the callback represents 
  an error.
- *minTimeout* and *maxTimtout* -- used to coerce the result of the timeout
  function.
- *maxAttempts* -- the maximum number number of attempts before
  giving up and returning the last error.

Backoff Strategy
================

wip
