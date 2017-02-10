# Teamwork
Software Engineering Senior Design CS116/117 (UCSC Winter/Spring 2017)

# Setting up a development environment to contribute

## Step 1: Python Virtual Enviornment
Note: Python 3.6 is assumed. Check your python version with `python --version`
If you don't have [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) (it comes with python3 on some systems), install it with `pip install virtualenv`
Change to a directory where you want the teamwork-project directory to reside (e.g. `cd Documents/`)
Create a new venv (this will create a new folder with python installed and later django/dependencies)
```bash
$ virtualenv twdev
```
Note: you don't have to call your folder/venv "twdev"

Now cd into twdev (or whatever you named your venv) and activate it
```bash
$ source bin/activate
```
Note: you'll have to activate the venv anytime you want to work on this project. Consider adding 
