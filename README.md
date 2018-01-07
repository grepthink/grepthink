# TSR Assistant (UCSC Fall 2017 - CMPS 115-01)
A project that builds off of [grepthink](https://github.com/grepthink/grepthink/) that assists professors and teaching assistants in determining problematic teams and team members.

Project Documentation and Planning Notes can be found [here.](https://drive.google.com/drive/folders/0B1R1qp5QghphYndneXQ5LVQ2d2s?usp=sharing)

## Installation Instructions
Prerequisite: Python 3 must be installed. You can get that [here](https://www.python.org/downloads/)

1. Start by cloning our project with `git clone https://github.com/divark/tsrassistant.git`
2. Once downloaded, go into your main directory and proceed to make a .env file with the following contents:
```
SECRET_KEY=whateveryouwanthere
DEBUG=True
DATABASE_URL=sqlite:////tmp/db.sqlite3
```
3. Install the prerequisites needed to run the server with `pip install -r requirements.txt`
4. Run the following command: `python manage.py migrate`
5. Start the server up with `python manage.py runserver`
6. Pull up your web browser of choice, and connect to 127.0.0.1:8000.
