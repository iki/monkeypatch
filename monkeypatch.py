#!/usr/bin/env python
"""
monkeypatch
===========

Patches module object/class/function.

Package:
  http://pypi.python.org/pypi/monkeypatch
Project:
  https://github.com/iki/monkeypatch
Issues:
  https://github.com/iki/monkeypatch/issues
Updates:
  https://github.com/iki/monkeypatch/commits/master.atom
Install via `pip <http://www.pip-installer.org>`_:
  ``pip install monkeypatch``
Install via `easy_install <http://peak.telecommunity.com/DevCenter/EasyInstall>`_:
  ``easy_install monkeypatch``
Sources via `git <http://git-scm.com/>`_:
  ``git clone https://github.com/iki/monkeypatch``
Sources via `hg-git <https://github.com/schacon/hg-git>`_:
  ``hg clone git://github.com/iki/monkeypatch``
"""
__docformat__ = 'restructuredtext en'
__version__ = '0.1rc3'
__all__ = [ 'patch' ]

import sys

class ModuleProxy(type(sys)):
    """Module interface to a dictionary, e.g. locals().

    >>> module = ModuleProxy(locals())

    >>> a = 1
    >>> module.a
    1

    >>> module.b =2
    >>> b
    2

    >>> del a
    >>> module.a
    Traceback (most recent call last):
            ...
    AttributeError: a

    >>> del module.b
    >>> b
    Traceback (most recent call last):
            ...
    NameError: name 'b' is not defined
    """
    def __init__(self, data, name='<locals>'):
        object.__setattr__(self, '__data__', data)
        if not '__name__' in data:
            object.__setattr__(self, '__name__', name)

    def __getattr__(self, name):
        try:
            return self.__data__[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self.__data__[name] = value

    def __delattr__(self, name):
        del self.__data__[name]


def patch(new, module, target, store_as='_%(target)s',
    update_wrapper=True,
    sys_modules=False,
    **setattrs):
    """Patches module object/class/function.

    If module is True, then __builtin__.target is patched.

    If module is string, then sys.modules[module].target is patched
    and module is imported if it isn't in sys.modules already.

    If module is dictionary, module[target] is patched.

    If module is tuple, or list, or set, or space separated string
    of module names, then all modules are patched.

    Original module.target can be accessed via new._{target}
    attribute, or an attribute name passed as store_as.

    The new object attributes are updated using update_wrapper,
    or patch.update_wrapper, or functools.update_wrapper.

    If sys_modules is True (default) and module is object
    different from sys.modules[module.__name__],
    then sys.modules[module.__name__].target is patched as well.

    Returns True if module.target was already patched to new.

    >>> import logging
    >>> level = logging.root.level  # save
    >>> logging.root.setLevel(logging.DEBUG)

    >>> def _open(name, mode='r', buffering=-1, **options):
    ...     return 'open %s %s' % (name, dict(options, mode=mode))
    ...     # return _open._open(name, mode, buffering, **options)

    >>> import __builtin__
    >>> patch(_open, __builtin__, 'open')
    >>> open('/dev/zero')
    "open /dev/zero {'mode': 'r'}"
    >>> __builtin__.open = __builtin__.open._open  # restore

    >>> patch(_open, locals(), 'open')
    >>> open('/dev/zero')
    "open /dev/zero {'mode': 'r'}"
    >>> open = open._open  # restore

    >>> logging.root.setLevel(level)  # restore
    """
    self = patch
    # Import lazily.
    try:
        log = self.log
    except AttributeError:
        import logging
        log = self.log = logging

    if module is True:
        modname = '__builtin__'
        if not modname in sys.modules:
            import __builtin__
        module = sys.modules[modname]

    elif isinstance(module, basestring):
        if ' ' in module:
            module = module.split()
            return None not in [ patch(new, m, target, None, False, **setattrs)
                for m in module ] or None

        else:
            if not module in sys.modules:
                __import__(module)
            modname, module = module, sys.modules[module]

    elif isinstance(module, dict):
        module = ModuleProxy(module)
        modname = module.__name__

    elif isinstance(module, (tuple, list, set)):
        return None not in [ patch(new, m, target, None, sys_modules, **setattrs)
            for m in module ] or None

    else:
        modname = module.__name__
        sysmod = sys.modules.get(modname, None)
        if sysmod is module:
            pass
        elif sysmod is None:
            # self.log.debug('monkeypatch: missing sys.modules[%s]' % modname)
            pass
        elif sys_modules:
            # self.log.debug('monkeypatch: including sys.modules[%s]' % modname)
            patch(new, sysmod, target, store_as, False, **setattrs)
        else:
            self.log.debug('monkeypatch: skipping sys.modules[%s]' % modname)

    func = getattr(module, target, None)

    if func is new or ( func is not None
        and getattr(func, '__patch__module__', None) == new.__module__
        and getattr(func, '__patch__name__', None) == new.__name__):

        # self.log.debug('already patched: %s.%s (%s.%s) = %s.%s (%s.%s)' % (
        #    modname, target,
        #    getattr(getattr(func, '__patched__class__', None), '__module__', '?'),
        #    getattr(getattr(func, '__patched__class__', None), '__name__', '?'),
        #    getattr(func, '__patch__module__', new.__module__),
        #    getattr(func, '__patch__name__', new.__name__),
        #    new.__class__.__module__, new.__class__.__name__))

        return True

    else:
        self.log.info('patch: %s.%s (%s.%s) = %s.%s (%s.%s)' % (
            modname, target,
            func.__class__.__module__, func.__class__.__name__,
            new.__module__, new.__name__,
            new.__class__.__module__, new.__class__.__name__))

    new.__patch__name__ = new.__name__
    new.__patch__module__ = new.__module__
    new.__patched__class__ = func.__class__

    if func is not None:

        if update_wrapper:

            if not callable(update_wrapper):
                # Import lazily.
                try:
                    update_wrapper = self.update_wrapper
                except AttributeError:
                    import functools
                    update_wrapper = self.update_wrapper = functools.update_wrapper

            try:
                update_wrapper(new, func)
            except AttributeError:
                pass

        if store_as:
            if store_as.find('%(') != -1:
                store_as = store_as % dict(module=module.__name__, target=target)

            setattr(new, store_as, func)

    for k in setattrs:
        setattr(new, k, setattrs[k])

    setattr(module, target, new)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
