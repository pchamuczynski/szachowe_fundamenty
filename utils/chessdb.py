import sqlite3
from sqlite3 import Error

from utils import task, user, training
import random

class ChessDb:
    sql_init_tasks_table = """ CREATE TABLE tasks(
        id integer PRIMARY KEY AUTOINCREMENT,
        FEN text NOT NULL,
        chapter text NOT NULL,
        lesson integer NOT NULL,
        number integer NOT NULL,
        tags text,
        url text,
        comment text
    );"""
    
    sql_init_users_table = """ CREATE TABLE IF NOT EXISTS users(
        name text PRIMARY KEY
    );"""
    
    sql_init_training_table = """CREATE TABLE IF NOT EXISTS training(
        id integer PRIMARY KEY AUTOINCREMENT,
        task_id integer NOT NULL,
        user_name text NOT NULL,
        date datetime DEFAULT CURRENT_TIMESTAMP,
        comment text,
        
        FOREIGN KEY (task_id) REFERENCES tasks(id),
        FOREIGN KEY (user_name) REFERENCES users(name)
    );"""
    
    sql_init_favorites_table = """CREATE TABLE IF NOT EXISTS favorites(
        id integer PRIMARY KEY AUTOINCREMENT,
        task_id integer NOT NULL,
        user_name text NOT NULL,
        
        FOREIGN KEY (task_id) REFERENCES tasks(id),
        FOREIGN KEY (user_name) REFERENCES users(name),
        
        UNIQUE (task_id, user_name)
    );"""

    def __init__(self, db_file, tasks):
        self.connection = sqlite3.connect(db_file)
        
        self.__sql_query("DROP TABLE IF EXISTS tasks;")
        self.__sql_query(self.sql_init_tasks_table)
        self.__sql_query(self.sql_init_users_table)
        self.__sql_query(self.sql_init_training_table)
        self.__sql_query(self.sql_init_favorites_table)
        
        self.__sql_query("DELETE FROM tasks")
        id = 0
        for task in tasks:
            self.__sql_query('INSERT INTO tasks VALUES (' + str(id) + ',"' + task.FEN.strip() + '", "' + task.chapter + '", "' + task.lesson + '", ' + str(task.number) + ', "' + str(task.tags) + '", "' + task.url +'", "' + task.comment + '")')
            id +=1
            
        if(self.get_user('default') == None):
            print('Creating default user')
            self.__sql_query('INSERT INTO users VALUES default')
        self.connection.commit()

    def __del__(self):
        self.connection.close()
        
    def get_task_id(self, task):
        sql_query = "SELECT id FROM tasks WHERE FEN = '" + task.FEN.strip() + "' AND chapter = '" + task.chapter + "' AND lesson = '" + task.lesson + "' AND number = " + str(task.number)    
        result = self.__sql_query(sql_query)
        if result != None:
            return result[0][0]
    
    def get_task(self, task_id):
        sql_get_task = "SELECT * FROM tasks WHERE id = " + str(task_id)
        result = self.__sql_query(sql_get_task)
        if len(result) > 0:
            return task.Task(result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], result[0][6])
        return None

    def get_user(self, name):
        sql_get_task = "SELECT * FROM users WHERE name = '" + name + "'"
        result = self.__sql_query(sql_get_task)
        if result != None:
            return user.User([0][0])
        return None
        
    def get_new_tasks(self, user, count = 0, shuffle = False):
        sql_get_new_tasks = "SELECT * FROM tasks WHERE id NOT IN (SELECT task_id FROM training WHERE user_name = '" + user + "')"
        result = self.__sql_query(sql_get_new_tasks)
        tasks = []
        if result != None:
            for row in result:
                tasks.append(task.Task(row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
            if shuffle:
                random.shuffle(tasks)
            if count > 0:
                return tasks[:count]
        return tasks
    
    def get_favorite_tasks(self, user, count = 0, shuffle = False):
        sql_get_favorite_tasks = "SELECT * FROM tasks WHERE id IN (SELECT task_id FROM favorites WHERE user_name = '" + user + "')"
        result = self.__sql_query(sql_get_favorite_tasks)
        tasks = []
        if result != None:
            tasks = [task.Task(row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in result]
        if shuffle:
            random.shuffle(tasks)
        if count > 0:
            return tasks[:count]
        return tasks
        
    def get_solved_tasks(self, user, count = 0, shuffle = False):
        print('Getting ' +str(count)  + '  solved tasks for user ' + user)
        sql_get_solved_tasks = "SELECT * FROM tasks WHERE id NOT IN (SELECT task_id FROM favorites WHERE user_name = '" + user + "') AND id IN (SELECT task_id FROM training WHERE user_name = '" + user + "')"
        result = self.__sql_query(sql_get_solved_tasks)
        tasks = []
        if result != None:
            for row in result:
                tasks.append(task.Task(row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
            if shuffle:
                random.shuffle(tasks)
            if count > 0:
                return tasks[:count]
        return tasks
        
    def update_training(self, user, task, comment = ''):
        task_id = self.get_task_id(task)
        sql_query = "INSERT INTO training (task_id, user_name, comment) VALUES (" + str(task_id) + ", '" + user + "', '" + comment + "')"
        self.__sql_query(sql_query)
        self.connection.commit()

       
    def favorites(self, user):
        query = "SELECT * FROM favorites WHERE user_name = '" + user + "'"
        return [self.get_task(row[1]) for row in self.__sql_query(query)]
     
    def add_to_favorites(self, user, task):
        task_id = self.get_task_id(task)
        #check if task is already in favorites
        query = "SELECT * FROM favorites WHERE task_id = " + str(task_id) + " AND user_name = '" + user + "'"
        if len(self.__sql_query(query)) == 0:
            query = "INSERT INTO favorites (task_id, user_name) VALUES (" + str(task_id) + ", '" + user + "')"
            self.__sql_query(query)
            self.connection.commit()
            
    def remove_from_favorites(self, user, task):
        task_id = self.get_task_id(task)
        #check if task is in favorites
        result = self.__sql_query("SELECT * FROM favorites WHERE task_id = " + str(task_id) + " AND user_name = '" + user + "'")
        if len(result) > 0:
            self.__sql_query("DELETE FROM favorites WHERE task_id = " + str(task_id) + " AND user_name = '" + user + "'")
            self.connection.commit()
        
    def __sql_query(self, query):
        try:
            c = self.connection.cursor()
            c.execute(query)
            return c.fetchall()
        
        except Error as e:
            print(e)

