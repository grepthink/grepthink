# Setting up a development environment to contribute

## Step 1: Python Virtual Environment
Note: Python 3.6.0 is used. Check your python version with `python --version`

If you don't have [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) (it comes with python3 on some systems), install it with `pip install virtualenv`

Create a new venv (this will create a new folder with python installed and later django/dependencies)
```bash
$ virtualenv gtdev
```
Note: you don't have to call your folder/venv "gtdev"

Now cd into gtdev (or whatever you named your venv) and activate it
```bash
$ source bin/activate
```

For windows: cd into gtdev/Scripts and run activate.bat

Note: you'll have to activate the venv anytime you want to work on this project. Consider adding an alias to your .bash_profile or .bashrc
```bash
alias gt="cd ~/Documents/gtdev && source bin/activate"
```
You can always exit the venv with `deactivate`

## Step 2: Cloning the Repo
Optionally fork the grepthink repo. 

Clone the grepthink master branch.

https://github.com/grepthink/grepthink.git

## Step 3: Copy .env.example into .env

``cd``` into the grepthink folder.

Copy the example.env file

```cp etc/example.env .env```

open in your text enter of choice (for me `subl .env`).


Set the databse url for local development. Hint: use `pwd` and copy/paste.

For local develompent, your DATABASE_URL can be something like:
`DATABASE_URL=sqlite:////Users/sammyslug/Documents/gtdev/grepthink/teamwork/db.sqlite3`


## Step 4: Install dependencies
Make sure you're in your venv then install everything in requirements.txt
```bash
$ pip install -r requirements.txt
```

## Step 5: Test start
Try running with `python manage.py runserver`

## Step 6: Read Django docs and other docs in the grepthink repo

- migrations and the command makemigrations (https://docs.djangoproject.com/en/2.1/topics/migrations/)
- googling django...there's a lot out there.

## Step 7: Get in touch

Reach out on slack or through email: https://www.grepthink.com/contact/
