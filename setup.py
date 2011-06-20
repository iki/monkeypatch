#!/usr/bin/env python
from monkeypatch import __version__, __doc__, __docformat__

options = dict(
    minver = '2.5', # Min Python version required.
    maxver = None,  # Max Python version required.
    use_distribute = False,  # Use distribute_setup.py.
    use_stdeb = False,       # Use stdeb for building deb packages.
    )

properties = dict(
    name = 'monkeypatch',
    version = __version__,
    license = 'BSD',
    url = 'https://github.com/iki/monkeypatch',
    # download_url = 'https://github.com/iki/monkeypatch/tarball/v%s' % __version__,
    description = 'Monkey patcher',
    long_description = __doc__,
    author = 'Jan Killian',
    author_email = 'jan.killian@gmail.com',
    zip_safe = True,
    platforms = 'any',
    keywords = [
        'patch',
        'monkey-patch',
        ],
    py_modules = [
        'monkeypatch',
        ],
    packages = [
        ],
    namespace_packages = [
        ],
    include_package_data = False,
    install_requires = [
        ],
    extras_require = {
        },
    dependency_links=[
        ],
    entry_points = {
        },
    scripts=[
        ],
    classifiers = [
        # See http://pypi.python.org/pypi?:action=list_classifiers.
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )

def main(properties=properties, options=options, **custom_options):
    """Imports setup function and passes properties to it."""
    return init(**dict(options, **custom_options))(**properties)

def init(
    minver=None, maxver=None,
    use_distribute=False, dist='dist',
    use_stdeb=False,
    ):
    """Imports and returns setup function.

    If use_distribute is set, then distribute_setup.py is imported.

    If use_stdeb is set on a Debian based system,
    then module stdeb is imported.

    Stdeb supports building deb packages on Debian based systems.
    The package should only be installed on the same system version
    it was built on, though. See http://github.com/astraw/stdeb.
    """
    if not minver == maxver == None:
        import sys
        if not minver <= sys.version < (maxver or 'Any'):
            sys.stderr.write(
                '%s: requires python version in <%s, %s), not %s\n' % (
                sys.argv[0], minver or 'any', maxver or 'any', sys.version.split()[0]))
            sys.exit(1)

    if use_distribute:
        from distribute_setup import use_setuptools
        use_setuptools(to_dir=dist)
        from setuptools import setup
    else:
        try:
            from setuptools import setup
        except ImportError:
            from distutils.core import setup

    if use_stdeb:
        import platform
        if 'debian' in platform.dist():
            try:
                import stdeb
            except ImportError, e:
                pass

    return setup

if __name__ == '__main__':
    main()
