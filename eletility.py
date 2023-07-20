import os
import datetime, time
import sqlite3
from sqlite3 import Error
import json


######################## DB ########################
class DB:
    def __init__(self):
        pass

    def migrate(self, file):
        """
        connects to database ["name"] defined inside the file param, creates/updates the table to match the given param
        blueprint. Does not modify columns if a column with the same name already exits. Drops columns but does not
        drop tables.

        @param file: an input file describing a database in json format. Example:
        {
            "name" : "mydb",
            "table1" : {
                            "title" : "text",
                            "somevalue" : "real"
                        },
            "table2" : {
                            "balance" : "integer",
                            "somevalue" : "blob"
                        },
        }
        """
        content = open(file)
        blueprint_data = json.load(content)
        db_name = blueprint_data["name"]
        self.connect(db_name)

        for index, table in enumerate(blueprint_data):
            if index == 0:
                continue

            conf = {"id": "INTEGER PRIMARY KEY"}

            for column in blueprint_data[table]:
                conf[column] = blueprint_data[table][column].upper()

            # check if the table exists
            if not self.tableExists(table):
                # table doesn't exist, create it
                self.createTable(table, conf)
            else:
                # table exists, check columns
                table_info = self.tableInfo(table)

                for bp_column in conf:
                    found_flag = False

                    for db_column_info in table_info:
                        db_column = db_column_info[1]

                        if bp_column == db_column:
                            found_flag = True
                            break
                    if not found_flag:
                        # update the table
                        command = "ALTER TABLE {} ADD {} {}".format(table, bp_column, conf[bp_column])
                        self.cursor.execute(command)

                table_info = self.tableInfo(table)

                for db_column_info in table_info:
                    db_column = db_column_info[1]

                    if not db_column in conf.keys():
                        command = "ALTER TABLE {} DROP COLUMN {}".format(table, db_column)
                        self.cursor.execute(command)

                # table_info = self.tableInfo(table)
                # print("table_info", table_info)
                # if not column_key in 
                # if column[1] != list(conf.keys())[index]

                # exit()
        # self.createLib(db_name)

    # def createLib(self, db_name):
    #     F = Files()

    #     # main header comment
    #     content = "# THIS CODE IS GENERATED BY ELETILITY. FOR BUG REPORTS PLEASE CONTACT: iliyaalavy@gmail.com\n\n"

    #     # lib import
    #     content += "import eletility as ele\n\n"

    #     # connect to db
    #     content += "DB = ele.DB()\n"
    #     content += "DB.connect('{}')\n\n".format(db_name)

    #     libfile = (db_name + "_lib.py")    
    #     F.truncate(libfile)

    #     tables = self.tables()

    #     for table in tables:
    #         table = table[0]

    #         # table header comment
    #         content += "# {} functions\n\n".format(table)
    #         tableInfo = self.tableInfo(table)

    #         # insert function
    #         content += "def insert{}(dictValue):\n\tDB.insert('{}', dictValue)\n\tpass\
    #             \n\n".format(table, table)
    #         for info in tableInfo:
    #             column = info[1]

    #         # print(tableInfo)
    #         # exit()

    #     F.writeLine(libfile, content)

    #     pass

    def tableInfo(self, table):
        return self.conn.execute('PRAGMA TABLE_INFO({})'.format(table)).fetchall()

    def connect(self, db_file):
        """ connects to or creates a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
            return False
        self.conn = conn
        self.cursor = self.conn.cursor()
        return True

    def tables(self):
        """ returns a list containing all the table names """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return self.cursor.fetchall()

    def tableExists(self, key):
        """ returns true if the given table name exists"""
        tables = self.tables()
        for name in tables:
            if name[0] == key:
                return True
        return False

    def createTable(self, name, conf):
        """ creates a table """
        cmd = "CREATE TABLE IF NOT EXISTS {}(".format(name)
        for key, value in conf.items():
            cmd += "{} {}, ".format(key, value)
        cmd = cmd[:len(cmd) - 2]
        cmd += ")"
        self.cursor.execute(cmd)
        self.conn.commit()

    def insertUnique(self, table, values, condition=True):
        """ inserts a row to a table if a condition is met """
        keys = "("
        vals = ""
        for key in values:
            vals += "'{}', ".format(values[key])
            keys += "{}, ".format(key)
        vals = vals[:len(vals) - 2] + ""
        keys = keys[:len(keys) - 2] + ")"
        cmd = "INSERT INTO {0} {1} SELECT {2} WHERE NOT EXISTS (SELECT 1 FROM {0} WHERE {3})".format(table, keys, vals,
                                                                                                     condition)
        self.cursor.execute(cmd)
        self.conn.commit()

    def insertUniqueCol(self, table: str, col: str, values: list):
        """ inserts a row to a table if a single condition is met """
        uniqueVal = None
        keys = "("
        vals = "("
        for key in values:
            if key == col:
                uniqueVal = values[key]
            vals += "'{}', ".format(values[key])
            keys += "{}, ".format(key)
        vals = vals[:len(vals) - 2] + ")"
        keys = keys[:len(keys) - 2] + ")"
        cmd = "INSERT INTO {0} {1} SELECT {2} WHERE NOT EXISTS (SELECT 1 FROM {0} WHERE {3}='{4}')".format(table, keys,
                                                                                                           vals, col,
                                                                                                           uniqueVal)
        self.cursor.execute(cmd)
        self.conn.commit()

    def selectOne(self, table, condition="TRUE"):
        """ returns one rows of a given table which meets a given condition """
        cmd = "SELECT 1 from {0} WHERE {1}".format(table, condition)
        self.cursor.execute(cmd)
        return self.cursor.fetchone()

    def selectAll(self, table, condition="TRUE"):
        """ returns all the rows of a given table which meet a given condition """
        cmd = "SELECT * from {0} WHERE {1}".format(table, condition)
        self.cursor.execute(cmd)
        return self.cursor.fetchall()

    def rowExists(self, table, condition="TRUE"):
        """ determines if a row exits in a table with a given condition """
        cmd = "SELECT * from {0} WHERE {1}".format(table, condition)
        self.cursor.execute(cmd)
        if len(self.cursor.fetchall()) < 1:
            return False
        return True

    def insert(self, table, values):
        """ inserts a row to a table """
        keys = "("
        vals = "("
        for key in values:
            vals += "'{}', ".format(values[key])
            keys += "{}, ".format(key)
        vals = vals[:len(vals) - 2] + ")"
        keys = keys[:len(keys) - 2] + ")"
        cmd = "INSERT INTO {} {} VALUES {}".format(table, keys, vals)
        self.cursor.execute(cmd)
        self.conn.commit()

    def update(self, table, values, condition):
        """ inserts a row to a table """
        keyval = ""
        for key in values:
            keyval += "{} = '{}',".format(key, values[key])
        keyval = keyval[:len(keyval) - 1]
        cmd = "UPDATE {} SET {} WHERE {}".format(table, keyval, condition)

        self.cursor.execute(cmd)
        self.conn.commit()

    def delete(self, table, condition):
        """ deletes row(s) from a given table which meet a given condition """
        cmd = "DELETE FROM {} WHERE {}".format(table, condition)
        self.cursor.execute(cmd)
        self.conn.commit()


######################## PATHHELPER ########################

class PathHelper:
    def __init__(self):
        pass

    def absPath(self, file):
        """ returns the absolute path to a given relative path """
        return os.path.abspath(file)


######################## VALIDATOR ########################

class Validator:
    def __init__(self):
        pass

    def isTitle(self, title, required=False):
        if not required:
            return True
        elif len(title) > 1:
            return True

    def isDesc(self, desc, required=False):
        if not required:
            return True
        elif len(desc) > 1:
            return True

    def isStrDate(self, date, format, required=False):
        if not required:
            if len(date) < 1:
                return True
        try:
            datetime.datetime.strptime(date, format)
        except ValueError:
            return False
        return True

    def isStrYN(self, str, required=False):
        print(str)
        if not required:
            if len(str) < 1:
                return True
        elif str.lower() == "y" or str.lower() == "n":
            return True
        return False

    def isNum(self, str, required=False):
        if not required:
            if len(str) < 1:
                return False
        elif str.isnumeric():
            return True
        return False


######################## STRINGPROC ########################

class StringProc:
    pass


# def create_connection(path):


#     connection = None
#     try:
#         connection = sqlite3.connect(path)
#         print("Successfully Connected")

########################## FILES ##########################

class Files:
    def __init__(self):
        pass

    def truncate(self, file, create=True):
        """ truncates a given file (creates a file if it doesn't exist) """
        try:
            f = open(file)
            f.truncate()
        except IOError:
            if create:
                f = open(file, "w")
                f.close()
                return 1
            return 0
        return 1

    def writeLine(self, file, str, create=True):
        """ appends a line to a file """
        try:
            f = open(file, "a")
            f.write(str)
            f.write("\n")
        except IOError:
            if create:
                print("dd")
                f = open(file, "w+")
                print("ss")
                f.write(str)
                f.write("\n")
                f.close()
                return 1
            return 0
        finally:
            f.close()
        return 1

    def write(self, file, str, create=True):
        """ writes into a file (doesn't end the line)"""
        try:
            f = open(file, "a")
            f.write(str)
        except IOError:
            if create:
                f = open(file, "w+")
                f.write(str)
                f.close()
                return 1
            return 0
        finally:
            f.close()
        return 1

    def writeTruncate(self, file, str, create=True):
        """ truncates a file and writes into it """
        self.truncate(file, create)
        self.write(file, str)

    def lbreak(self, file, create=False):
        """ appends a line break to a file """
        try:
            f = open(file, "a")
            f.write("\n")
        except IOError:
            if create:
                f = open(file, "w+")
                f.write("\n")
                f.close()
                return 1
            return 0
        finally:
            f.close()
        return 1
        pass


########################## Times ##########################

class Times:
    def __init__(self):
        """ Date time helper functions"""
        pass

    def monthS2N(self, month):
        """ converts a month string to its corresponding numberical value """
        month = month.lower()
        if month == "jan" or month == "january":
            return "01"
        elif month == "feb" or month == "february":
            return "02"
        elif month == "mar" or month == "march":
            return "03"
        elif month == "apr" or month == "april":
            return "04"
        elif month == "may" or month == "may":
            return "05"
        elif month == "jun" or month == "june":
            return "06"
        elif month == "jul" or month == "july":
            return "07"
        elif month == "aug" or month == "august":
            return "08"
        elif month == "sep" or month == "september":
            return "09"
        elif month == "oct" or month == "october":
            return "10"
        elif month == "nov" or month == "november":
            return "11"
        elif month == "dec" or month == "december":
            return "12"
        else:
            raise "invalid month"

    def now(self):
        now = datetime.datetime.now().time()
        return now.strftime('%H:%M:%S')

    def substract(self, endtime, starttime):
        date = datetime.date(1, 1, 1)
        startDateTime = datetime.datetime.combine(date, starttime)
        endDateTime = datetime.datetime.combine(date, endtime)
        diff = endDateTime - startDateTime
        return diff


########################## ConfigParser ##########################

class ConfigParser:
    """ Config parser constructor """

    def __init__(self):
        pass

    """ reads from a given config file and returns a list of the arguements """

    def read(self, path):
        config = {}
        try:
            file = open(path, 'r')
        except IOError as e:
            raise Exception(e.strerror)

        lines = file.readlines()
        for num, line in enumerate(lines):
            line = line.split("#")[0].strip()

            if len(line) == 0:
                # empty line, ignore
                continue
            elif line[0] == "#":
                # comment
                continue
            else:
                tokens = line.split("=", 1)
                if len(tokens) < 2:
                    # illegal length
                    msg = "Illegal format on line " + str(num+1) + " of " + file.name
                    raise Exception(msg)
                else:
                    # legal format
                    config[tokens[0].strip()] = tokens[1].strip()

        return config

    def write(self, config, path):
        with open(path, "w+") as file:
            file.truncate()
            for key in config:
                file.write(f"{key} = {config[key]}\n")



########################## Colors ##########################

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    DEBUG = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


########################## Log ##########################

class Log:
    def __init__(self, level="info", prefix=None) -> None:
        # if level == "warning":
        #     level = logging.WARNING
        # elif level == "debug":
        #     level = logging.DEBUG
        # else:
        #     level = logging.WARNING
        self.level = level
        self.prefix = prefix
        pass

    def Gprint(self, msg):
        print(Colors.OKGREEN, msg, Colors.ENDC, end="")

    def Rprint(self, msg):
        print(Colors.ERROR, msg, Colors.ENDC, end="")

    def Dprint(self, msg):
        print(Colors.DEBUG, msg, Colors.ENDC, end="")

    def Yprint(self, msg):
        print(Colors.WARNING, msg, Colors.ENDC, end="")

    def Hprint(self, msg):
        print(Colors.HEADER, msg, Colors.ENDC, end="")

    def Boldprint(self, msg):
        print(Colors.BOLD, msg, Colors.ENDC, end="")

    def Bprint(self, msg):
        print(Colors.OKBLUE, msg, Colors.ENDC, end="")

    def alive_print(self, message):
        for char in message:
            print(char, end="", flush=True)
            time.sleep(0.03)
        print("")

    def D(self, message):
        time = Times().now()
        if not self.prefix is None:
            message = "{}:{}".format(self.prefix, message)
        message = "{}:{}".format(time, message)
        if self.level == "debug":
            print(Colors.DEBUG, message, Colors.ENDC)

    def W(self, message):
        time = Times().now()
        if not self.prefix is None:
            message = "{}:{}".format(self.prefix, message)
        message = "{}:{}".format(time, message)
        if self.level == "warning" or "debug" or "info":
            print(Colors.WARNING, message, Colors.ENDC)

    def I(self, message):
        time = Times().now()
        if not self.prefix is None:
            message = "{}:{}".format(self.prefix, message)
        message = "{}:{}".format(time, message)
        if self.level == "warning" or "debug" or "info":
            print(Colors.OKGREEN, message, Colors.ENDC)

    def E(self, message):
        time = Times().now()
        if not self.prefix is None:
            message = "{}:{}".format(self.prefix, message)
        message = "{}:ERROR:{}".format(time, message)
        if self.level == "warning" or "debug" or "info":
            print(Colors.ERROR, message, Colors.ENDC)
        exit()


########################## List ##########################

class List:
    def __init__(self) -> None:
        pass
