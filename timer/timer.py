import argparse
import os
import sqlite3
import sys
from datetime import datetime

ENV = ".env"

SCHEMA = (
    "CREATE TABLE activities ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
    "activity TEXT NOT NULL);", 
    "CREATE TABLE times ("
    "time_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
    "activity_id INTEGER, "
    "start TEXT, "
    "stop TEXT, "
    "FOREIGN KEY(activity_id) REFERENCES activities(id));"
)

DATETIME_FORMAT = "%d-%m-%Y %H:%M:%S"

def _get_current_time():
    return datetime.now().strftime(DATETIME_FORMAT)

def _get_datetime(datetime_str):
    return datetime.strptime(stopping_time, DATETIME_FORMAT)

def _get_duration(starting_time, stopping_time):
    duration = datetime.strptime(stopping_time, DATETIME_FORMAT) \
        - datetime.strptime(starting_time, DATETIME_FORMAT)
    return duration 

parser = argparse.ArgumentParser(description="Times your activities.")

# allow users to create sqlite3 database file and overwrite it if necessary
parser.add_argument("-i", "--init", type=str)
parser.add_argument("-o", "--overwrite", action="store_true")

# lets users start/stop the timer and to add a new activity if not yet exists
parser.add_argument("--start", "-s", type=str)
parser.add_argument("-n", "--new", action="store_true")

args = parser.parse_args()

if args.init:
    # check if database file already exists
    files = os.listdir()
    database = args.init
    if database in files and not args.overwrite:
        raise argparse.ArgumentTypeError(
            f"The file '{database}' already exists. "
            "Set [-o, --overwrite] to overwrite."
        )

    # create the database file using the specified name
    with open(database, "w") as fp:
        with sqlite3.connect(database) as con:
            cur = con.cursor()
            for statement in SCHEMA: 
                cur.execute(statement)

    # check if env file already exists
    if ENV in files and not args.overwrite:
        raise argparse.ArgumentTypeError(
            f"The file '{ENV}' already exists. "
            "Set [-o, --overwrite] to overwrite."
        )

    # create an .env file containing the name of the database file
    with open(ENV, "w") as fp:
        fp.write(database)

if args.start:
    # retrieve or create to be inserted values
    activity = args.start
    starting_time = _get_current_time()

    # read environment file to retrieve database name
    with open(ENV) as fp:
        database = fp.read()

    # check if activity already exists
    with sqlite3.connect(database) as con:
        cur = con.cursor()
        cur.execute("SELECT activity FROM activities;")
        activities = cur.fetchall()
        activities = [activity[0] for activity in activities]

    if activity not in activities:
        # activity doesn't yet exist but user doesn't want to add new one
        if not args.new:
            raise argparse.ArgumentTypeError(
                f"The activity '{activity}' does not yet exist in the database. "
                f"Choose one of the following stored activities: {activities} "
                f"or add a new one using [-n, --new]."
            )
        # activity doesnt yet exist but user wants to add it
        else:
            # add the activity to the activities table
            with sqlite3.connect(database) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO activities (activity) VALUES (?);", (activity, ))
                con.commit()
    else:
        if args.new:
            raise argparse.ArgumentTypeError(
                f"The activity '{activity}' already exists in the database. "
                "The argument [-n, --new] is not required."
        )

    # retrieve the actitivity's id to correctly insert
    with sqlite3.connect(database) as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM activities WHERE activity = ?", (activity, ))
        activity_id = cur.fetchone()[0]

    # add current time to times table now that activity exists
    with sqlite3.connect(database) as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO times (activity_id, start, stop) VALUES (?, ?, ?);",
            (activity_id, starting_time, "TBD")
        )

    # let user know timer has started and provide stopping instructions
    print(f"Timer started for activity '{activity}' at {starting_time}.")
    print("Stop timer by pressing [CTRL] + [C].")

    # listen to keyboardinterrupt, then stop timer
    try:
        while True:
            pass
    # user wants to stop timer
    except KeyboardInterrupt:

        # what's the stopping time, i.e. current time?
        stopping_time = _get_current_time()

        # update the activity by including the stopping time
        with sqlite3.connect(database) as con:
            cur = con.cursor()

            # which activity needs to be updated?
            cur.execute("SELECT MAX(time_id) FROM times;")
            time_id = cur.fetchone()[0]
        
            # update last row adding stopping time
            cur.execute(
                "UPDATE times set STOP = ? WHERE time_id = ?;",
                (stopping_time, time_id)
            )
            con.commit()

        # calculate how long the activity lasted to include in printout
        datetime_duration = _get_duration(starting_time, stopping_time)
        
        # update user that timer has stopped
        print(
            f"Timer stopped for activity '{activity}' at {stopping_time}. "
            f"The activity lasted {datetime_duration}."
        )
        
        # prevent traceback
        try:
            sys.exit(1)
        except SystemExit:
            os._exit(1)
