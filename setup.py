from setuptools import setup, Command
import subprocess


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call(['py.test'])
        raise SystemExit(errno)


setup(
    name='Flask-Test',
    version='0.1.5',
    url='http://github.com/kvesteri/flask-test',
    license='MIT',
    author='Konsta Vesterinen',
    author_email='konsta.vesterinen@gmail.com',
    description='Various unit testing helpers for Flask applications.',
    long_description='Various unit testing helpers for Flask applications.',
    packages=['flask_test'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.7',
        'SQLAlchemy>=0.7.8'
    ],
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
