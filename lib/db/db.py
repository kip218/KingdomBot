import sys
from psycopg2 import connect
from apscheduler.triggers.interval import IntervalTrigger
from os.path import isfile

# importing database_url
sys.path.append("../../")
from settings import DATABASE_URL

BUILD_PATH = "./lib/db/build.sql"

# initiate database connection
conn = connect(DATABASE_URL, sslmode="require")
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


# fetch field
def field(command, *values):
    cur.execute(command, tuple(values))
    if (fetch := cur.fetchone()) is not None:
        return fetch[0]


# fetch row
def record(command, *values):
    cur.execute(command, tuple(values))
    return cur.fetchone()


# fetch rows
def records(command, *values):
    cur.execute(command, tuple(values))
    return cur.fetchall()


# fetch column
def column(command, *values):
    cur.execute(command, tuple(values))
    return [item[0] for item in cur.fetchall()]


# execute SQL command
def execute(command, *values):
    cur.execute(command, tuple(values))


# execute SQL script (for building database)
def scriptexec(path):
    with open(path, "r", encoding="utf-8") as script:
        cur.execute(script.read())


"""
Specific commands for users
"""


def add_user(userID, username):
    execute(
        "INSERT INTO users (UserID, Username) VALUES (%s, %s) ON CONFLICT (UserID) DO NOTHING;",
        userID,
        username,
    )


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
        execute(
            "UPDATE users SET Balance = Balance - %s WHERE UserID = %s", amount, userID
        )


def change_kingdom_name(userID, kingdom_name):
    execute("UPDATE users SET KingdomName = %s WHERE UserID = %s", kingdom_name, userID)


def change_kingdom_emblem(userID, kingdom_emblem):
    execute(
        "UPDATE users SET KingdomEmblem = %s WHERE UserID = %s", kingdom_emblem, userID
    )


def get_army(userID):
    return field("SELECT Army FROM users WHERE UserID = %s", userID)


def get_armysize(userID):
    army = get_army(userID)
    if army is None:
        return 0
    size = 0
    for unit in army:
        size += int(unit[1])
    return size


def get_unit(userID, unit_name):
    army = get_army(userID)
    if army is None:
        return None, None
    for unit in army:
        if unit_name == unit[0]:
            return unit[0], unit[1]
    return None, None


def add_unit(userID, unit_to_add):
    army = get_army(userID)
    if army is None:
        army = [[unit_to_add, "1"]]
        execute("UPDATE users SET Army = %s WHERE UserID = %s", army, userID)
        return
    unit_name, unit_count = get_unit(userID, unit_to_add)
    if unit_name and unit_count:
        for unit in army:
            if unit_name == unit[0]:
                unit[1] = str(int(unit[1]) + 1)
    else:
        army.append([unit_to_add, "1"])
    execute("UPDATE users SET Army = %s WHERE UserID = %s", army, userID)


def add_units(userID, unit_lst):
    for unit in unit_lst:
        add_unit(userID, unit)


def reset_army(userID):
    execute("UPDATE users SET Army = DEFAULT WHERE UserID = %s", userID)


def add_reminder(reminderID, task, reminderTime, userID, channelID):
    execute(
        "INSERT INTO Reminders (ReminderID, Task, ReminderTime, UserID, ChannelID) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (ReminderID) DO NOTHING;",
        reminderID,
        task,
        reminderTime,
        userID,
        channelID,
    )


def get_reminders(now):
    return records(
        "SELECT ReminderID, Task, UserID, ChannelID FROM Reminders WHERE ReminderTime::timestamptz <= %s::timestamptz",
        now,
    )


def remove_reminder(reminderID):
    execute("DELETE FROM Reminders WHERE ReminderID = %s", reminderID)


"""
Specific commands for servers
"""


def add_server(serverID):
    execute(
        "INSERT INTO servers (ServerID) VALUES (%s) ON CONFLICT (ServerID) DO NOTHING;",
        serverID,
    )


def remove_server(serverID):
    execute("DELETE FROM servers WHERE ServerID = %s", serverID)


def get_prefix(serverID):
    return field("SELECT Prefix FROM Servers WHERE ServerID = %s", serverID)


def change_prefix(serverID, prefix):
    execute("UPDATE servers SET Prefix = %s WHERE ServerID = %s", prefix, serverID)
