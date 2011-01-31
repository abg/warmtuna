from setuptools import setup, find_packages

version = '1.0'

setup(name='warmtuna',
    version=version,
    description="mysql warm backup plugin for holland",
    long_description="""\
""",
    classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Andrew Garner',
    author_email='muzazzi@gmail.com',
    url='http://hollandbackup.org',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      # -*- Extra requirements: -*-
    ],
    entry_points="""
    [holland.backup]
    warmtuna = holland.backup.warmtuna:WarmTuna
    """,
    namespace_packages=['holland', 'holland.backup']
)
