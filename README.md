# nxpush

This is a small python program for pushing files on a nuxeo repository when fs events are detected

##### requires

python2.7

pyinotify

#### install pyinotify (using pip)

apt-get install python-pip python-dev build-essential
pip install --upgrade pip
pip install setuptools --no-use-wheel –upgrade
pip install pyinotify


trivial init.d is comming with the sources

configuration is to be made in nx-properties.xml

credentials.xml should be an xml file with the following structure

+credentials+

+--user: nuxeo username --+

+--password: nuxeo password --+

