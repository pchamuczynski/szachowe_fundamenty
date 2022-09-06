#!/usr/bin/python3

import argparse, random
import sqlite3
from sqlite3 import Error
import chess, chess.svg

class Task:
    def __init__(self, tuple):
        self.__init__(self, tuple[1], tuple[2], tuple[3], tuple[4], tuple[5], tuple[6])
        
    def __init__(self, fen, chapter, lesson, number, tags, comment):
        self.FEN = fen
        self.chapter = chapter
        self.lesson = lesson
        self.number = number
        self.tags = tags
        self.comment = comment     
        # print('Task created ' + str(self))
    
    def __str__(self):
        return self.FEN + '\t(Chapter: ' + self.chapter + ', Lesson: ' + self.lesson + ', Task number: ' + str(self.number) + ', Tags: ' + str(self.tags) + ', Comment: ' + self.comment +')'       
    
def parse_file(filename):
    tasks = []

    curreent_chapter = 'undefined'
    current_lesson = 'undefined'
    current_tags = []
    file = open(filename, 'r')
    for line in file.readlines():
        line = line.strip()
        if line.startswith('# '):
            curreent_chapter = line[2:]
            # print('Parsing chapter ' + curreent_chapter)
        if line.startswith('## '):
            current_lesson = line[3:]
            current_tags = []
            # print('Parsing lesson: ' + current_lesson + ' in chapter ' + curreent_chapter)
        if line.startswith('[') and line.endswith(']'):
            tags = line[1:len(line) - 1]
            current_tags = [tag.strip() for tag in tags.split(',')]
            # print('current tags: ' + str(current_tags))
        if line.split('.')[0].isdigit(): #lines starting with a number shall cotain a task
            task_number = int(line.split('.')[0])
            task_tags_substr = line[line.find('['):line.find(']') + 1]
            task_comment = line.split('//')[1].replace(task_tags_substr, '') if '//' in line else ''            
            task_tags = [tag.strip() for tag in task_tags_substr[1:len(task_tags_substr) - 1].split(',') if tag.strip() != ''] + current_tags
            fen = line.split('.')[1].split('//')[0]
            
            tasks.append(Task(fen, curreent_chapter, current_lesson, task_number, task_tags, task_comment))            
        
    return tasks

def parse_args():
    parser = argparse.ArgumentParser(prog='szachy', description='chess drill') 
    
    parser.add_argument('--input', action='store', help='file with tasks', default='szachowe_fundamenty.txt')
    parser.add_argument('--count', dest='count', action='store', type=int, help='Number of returned tasks')
    parser.add_argument('--chapter', dest='chapter', action='store', help='use only tasks from given chapter')
    parser.add_argument('--lesson', dest='lesson', action='store', help="use only tasks from given lesson. Provide just the lesson's number")
    parser.add_argument('--task_number', dest='task_number', action='store', help='use only tasks with given number')
    parser.add_argument('--tags', dest='tags', action='store', help='use only tasks with given tags (separated by a comma and no spaces. put quotes around it, if tags contain spaces)')
    parser.add_argument('--shuffle', dest='shuffle', action='store_true', help='Shuffle the result before use')
    parser.add_argument('--drill', dest='drill', action='store_true', help='Your daily drill')
    parser.add_argument('--user', dest='user', action='store', help='Your name', default='default')
    parser.add_argument('--db_file', dest='db_file', action='store', help='Name of the database file', default='szachy.db')
    
    return vars(parser.parse_args())

def filter_tasks(tasks, filters):
    result = tasks
    if filters['chapter'] != None:
        result = [task for task in result if task.chapter.split('.')[0] == filters['chapter']]
    if filters['lesson'] != None:
        result = [task for task in result if int(task.lesson.split('.')[0]) == int(filters['lesson'])]
    if filters['task_number'] != None:
        result = [task for task in result if task.number == int(filters['task_number'])]
    if filters['tags'] != None:
        tags = [tag.strip() for tag in filters['tags'].split(',')]
        result = [task for task in result if all([tag in task.tags for tag in tags])]       
    if filters['shuffle']:
        random.shuffle(result)
    if filters['count'] != None:
        result = result[0:filters['count']]
        
    print(result)
    return result  


def sql_query(connection, query):
    try:
        c = connection.cursor()
        c.execute(query)
        return c.fetchall()
    
    except Error as e:
        print(e)

def init_db(tasks, connection):
    sql_init_tasks_table = """ CREATE TABLE IF NOT EXISTS tasks(
        id integer PRIMARY KEY,
        FEN text NOT NULL,
        chapter text NOT NULL,
        lesson integer NOT NULL,
        number integer NOT NULL,
        tags text,
        comment text
    );"""
    sql_query(connection, sql_init_tasks_table)
    sql_query(connection, "DELETE FROM tasks")
    id = 0
    for task in tasks:
        sql_query(connection, 'INSERT INTO tasks VALUES (' + str(id) + ',"' + task.FEN.strip() + '", "' + task.chapter + '", "' + str(task.lesson) + '", ' + str(task.number) + ', "' + str(task.tags) + '", "' + task.comment + '")')
        id +=1
        
    sql_training_record_table = """CREATE TABLE IF NOT EXISTS training(
        id integer PRIMARY KEY,
        task_id integer NOT NULL,
        date text NOT_NULL,
        score integer not null,
        FOREIGN KEY (task_id) REFERENCES tasks (id)
        );"""
    sql_query(connection, sql_training_record_table)
    connection.commit()

def get_task(connection, task_id):
    sql_get_task = """SELECT * FROM tasks WHERE id = """ + str(task_id)
    result = sql_query(connection, sql_get_task)
    if len(result) > 0:
        return Task(result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], result[0][6])
    return None

def select_task(connection, **filter):
    sql_select_new_task = """ SELECT id FROM tasks WHERE id NOT IN
        (SELECT task_id FROM training);"""
    result = sql_query(connection, sql_select_new_task)
    random.shuffle(result)
    return get_task(connection, result[0][0])


def drill(tasks, db_file, user):
    try:
        connection = sqlite3.connect(db_file)
        init_db(tasks, connection)
        task = select_task(connection)
        board = chess.Board(task.FEN)
        boardsvg = chess.svg.board(board=board)
        f = open("file.svg", "w")
        f.write(boardsvg)
        f.close()
        
    except Error as e:
        print("Error in init_db")
        print(e)
        
    finally:
        connection.close()

def main():
    args = parse_args()
    tasks = parse_file(args['input'])

    if args['drill']:
        drill(tasks, args['db_file'], args['user'])
    else:
        tasks = filter_tasks(tasks, args)
        [print(task) for task in tasks]
        
    
if __name__ == '__main__':
    main()

