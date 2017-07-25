Setup and Installation
=====


# Setting up a development environment to contribute

## Step 1: Python Virtual Enviornment
Note: Python 3.6 is assumed. Check your python version with `python --version`

If you don't have [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) (it comes with python3 on some systems), install it with `pip install virtualenv`

Change to a directory where you want the teamwork-project directory to reside (e.g. `cd Documents/`)

Create a new venv (this will create a new folder with python installed and later django/dependencies)
```bash
$ virtualenv my_venv
```
For "my_venv" you can choose whatever name you'd prefer

Now cd into my_venv, or whatever you chose to name your virtual environment, and activate it
```bash
$ source bin/activate
```

For windows: cd into my_venv/Scripts and run activate.bat

Note: you'll have to activate the venv anytime you want to work on this project. Consider adding an alias to your .bash_profile or .bashrc
```bash
alias tw="cd ~/Documents/my_venv && source bin/activate"
```
You can always exit the venv with `deactivate`

## Step 2: Cloning the Repo
Optionally fork the teamwork-project repo. Clone it into the venv folder you just created. That's it, have a cookie.

## Step 3: Make a .env file based on .env.example
The .env file should be in the my_venv (or whatever you named your venv) folder. So above the teamwork-project folder.

This is so we can keep the secret key hidden. 

It also allows us to use sqlite locally and postgres in production, neat.

For local develompent, your DATABASE_URL can be something like:
`DATABASE_URL=sqlite:////Users/sammyslug/Documents/my_venv/teamwork-project/teamwork/db.sqlite3`

The .env file should be in /my_venv/teamwork-project


## Step 4: Install dependencies
This part is fun because it's easy. Make sure you're in your venv then install everything in requirements.txt
```bash
$ pip install -r requirements.txt
```

## Step 5: Database Initialization
Now you will have to make the appropriate tables in your database using
```
python manage.py makemigrations auth courses profiles projects
```
and then you can migrate these migrations using `python manage.py migrate`

## Step 6: Running the server
You can run the server using `python manage.py runserver`