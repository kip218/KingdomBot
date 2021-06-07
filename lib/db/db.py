import sys
from psycopg2 import connect
from apscheduler.triggers.interval import IntervalTrigger
from os.path import isfile

#importing database_url
sys.path.append('../../')
from settings import DATABASE_URL

BUILD_PATH = './lib/db/build.sql'

#initiate database connection
conn = connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()
    return inner


@with_commit
def build():
    if isfile(BUILD_PATH):
        scriptexec(BUILD_PATH)


def commit():
    conn.commit()


def autosave(sched):
    sched.add_job(commit, IntervalTrigger(seconds=1))


def close():
    conn.close()


#fetch field
def field(command, *values):
    cur.execute(command, tuple(values))
    if (fetch := cur.fetchone()) is not None:
        return fetch[0]


#fetch row
def record(command, *values):
    cur.execute(command, tuple(values))
    return cur.fetchone()


#fetch rows
def records(command, *values):
    cur.execute(command, tuple(values))
    return cur.fetchall()


#fetch column
def column(command, *values):
    cur.execute(command, tuple(values))
    return [item[0] for item in cur.fetchall()]


#execute SQL command
def execute(command, *values):
    cur.execute(command, tuple(values))


#execute SQL script (for building database)
def scriptexec(path):
    with open(path, 'r', encoding='utf-8') as script:
        cur.execute(script.read())


"""
Specific commands
"""
# check if userID in database
def user_exists(userID):
    return bool(record("SELECT UserID FROM users WHERE UserID = %s", userID))


def get_balance(userID):
    return field("SELECT Balance FROM users WHERE UserID = %s", userID)


def add_balance(userID, amount):
    execute("UPDATE users SET Balance = Balance + %s WHERE UserID = %s", amount, userID)


def deduct_balance(userID, amount):
    curr_bal = get_balance(userID)
    if curr_bal < amount:
        return False
    else:
        execute("UPDATE users SET Balance = Balance - %s WHERE UserID = %s", amount, userID)
