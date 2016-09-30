ABOUT
-----
This is a full-featured Python client library for the Kyoto Tycoon server,
supporting both Python 2 and 3. It includes significant improvements over
the original library by Toru Maesaka and Stephen Hamer, but also introduces
some differences in API behavior.

Since the development of Kyoto Tycoon by its original authors seems to have
halted around 2012, we're also maintaining an updated and ready-to-go fork
of it here:

   https://github.com/alticelabs/kyoto

For more information on Kyoto Tycoon server, please refer to:

   http://alticelabs.github.io/kyoto/kyototycoon/doc/


FEATURES
--------
The more efficient binary protocol is also supported along with
the HTTP protocol. It provides a performance improvement of up
to 6x, but only the following operations are available:

  * ``get()`` and ``get_bulk()``
  * ``set()`` and ``set_bulk()``
  * ``remove()`` and ``remove_bulk()``
  * ``play_script()``

Atomic operations aren't supported with the binary protocol,
the use of "atomic=False" is mandatory when using it. Operations
besides these will raise a ``NotImplementedError`` exception.

It's possible to have two KyotoTycoon objects open to the same
server in the same application, one using HTTP and the other
using the binary protocol, if necessary.

The library does automatic packing and unpacking (marshalling)
of values coming from/to the database. The following data
storage formats are available by default:

  * ``KT_PACKER_PICKLE`` - Python "pickle" format.
  * ``KT_PACKER_JSON`` - JSON format (compact representation).
  * ``KT_PACKER_STRING`` - Strings (UTF-8).
  * ``KT_PACKER_BYTES`` - Binary data.

There is also a ``KT_PACKER_CUSTOM`` format available where you
can specify your own object to do the marshalling. This object
needs to provide the following two methods:

  * ``.pack(self, data)`` - convert "data" to ``bytes()``
  * ``.unpack(self, data)`` - convert "data" from ``bytes()``

Marshalling is done for all methods except ``play_script()``,
because the server can return data in more than one format at
once. The caller will most likely know the type of data that
the called script returns and must do the marshalling itself.


REPLICATION SLAVE
-----------------
Since version 0.7.0 this library also contains a replication slave
class. This class provides a ``consume()`` generator function that
receives and parses transaction log entries from a Kyoto Tycoon
master server into dictionaries.

This can be used to build your own custom replication schemes,
like key filtering, or react to server "set", "remove" or "clear"
database operations.

Do note that only explicit operations create transaction log events.
Implicit operations like key removal upon expiration don't.

Unlike the client library, the replication slave always handles the
"key" and "value" attributes as opaque binary data.


MEMCACHE-ENABLED SERVERS
------------------------
Kyoto Tycoon supports a subset of the memcached protocol. When a
server has this enabled including item flags, these are stored as
the last 4 bytes of the value. Since version 0.7.3 of this library,
there's a custom packer included that transparently handles this and
also includes gzip compression/decompression for scenarios where,
for example, a Python application is writing HTML pages to the Kyoto
server and an HTTP server is reading from it using a memcached client
library.

Example::

    from kyototycoon import KyotoTycoon, KT_PACKER_CUSTOM
    from kyototycoon.packers import MemcachePacker

    mp = MemcachePacker(gzip_enabled=True, gzip_flag=1)
    kt = KyotoTycoon(pack_type=KT_PACKER_CUSTOM, custom_packer=mp)

    kt.open("127.0.0.1", 1978)

    kt.set("key", "value")
    value = kt.get("key")

    kt.close()

To handle ``(value, flags)`` pairs without any additional processing,
the ``SimpleMemcachePacker`` can be used::

    from kyototycoon import KyotoTycoon, KT_PACKER_CUSTOM
    from kyototycoon.packers import SimpleMemcachePacker

    smp = SimpleMemcachePacker()
    kt = KyotoTycoon(pack_type=KT_PACKER_CUSTOM, custom_packer=smp)

    kt.open("127.0.0.1", 1978)

    kt.set("key", ("value", 123))
    value, flags = kt.get("key")

    kt.close()


COMPATIBILITY
-------------
This library is still not at version 1.0, which means the API and
behavior are not guaranteed to remain consistent between versions.

Support for using an error object has been removed. If you need
the old behavior for compatibility reasons, use a version up to
(and including) v0.5.9. Versions later than this raise exceptions
on all Kyoto Tycoon errors.


INSTALLATION
------------
You can install the latest version of this library from source::

    python setup.py build
    python setup.py install

Or, you can install the latest stable release from PyPI::

    pip install python-kyototycoon-ng


RUNNING TESTS
-------------
To run tests, you need to start a Kyoto Tycoon server on port ``11978``
with two databases ``one`` and ``two``::

    # Runnig Kyoto Tycoon server as daemon
    # See http://alticelabs.github.io/kyoto/kyototycoon/doc/command.html#ktserver for more info
    /usr/local/bin/ktserver \
        -host 127.0.0.1 \
        -port 11978 \
        -pid your-kyoto-folder/kyoto.pid \
        -log your-kyoto-folder/ktserver.log \
        -oat \
        -dmn \  # Set as daemon
        your-kyoto-folder/db/one.kct \
        your-kyoto-folder/db/two.kct


Then run python file ``tests/t_all.py``::

    python tests/t_all.py


AUTHORS
-------
  * Carlos Rodrigues <cefrodrigues@gmail.com> (current maintainer)
  * Toru Maesaka <dev@torum.net>
  * Stephen Hamer <stephen.hamer@upverter.com>

Binary protocol support was added based on Ulrich Mierendorff's code.
You can find the original library at the following URL:

  http://www.ulrichmierendorff.com/software/kyoto_tycoon/python_library.html
