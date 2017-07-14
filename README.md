# Linux setup

```bash
$ sudo apt-get install gcc libsdl2-dev libffi-dev python-dev libomp-dev
```

# Project setup

```bash
$ mkvirtualenv thermogo
$ pip install -r requirements.txt
$ python setup.py develop # so we can do absolute imports
$ python thermogo/__init__.py
```