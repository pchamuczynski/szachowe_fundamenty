#!/usr/bin/python3

import argparse, random
from sqlite3 import Error
import tkinter
import chess, chess.svg
from utils.chessdb import ChessDb
from utils.task import Task
import sys
from enum import Enum
import keyboard
        
def parse_file(filename):
    tasks = []

    curreent_chapter = 'undefined'
    current_lesson = 'undefined'
    current_tags = []
    url = ''
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
        if line.startswith('url:'):
            url = line[4:]
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
            
            tasks.append(Task(fen, curreent_chapter, current_lesson, task_number, task_tags, url, task_comment))            
        
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
    parser.add_argument('--training', dest='training', action='store_true', help='Your daily training')
    parser.add_argument('--user', dest='user', action='store', help='Your name', default='default')
    parser.add_argument('--db_file', dest='db_file', action='store', help='Name of the database file', default='szachy.db')
    parser.add_argument('--solved', dest='solved', action='store', help="Number of solved tasks to be displayed in the training mode", default=5)
    parser.add_argument('--new', dest='new', action='store', help="Number of new tasks to be displayed in the training mode", default=5)
    parser.add_argument('--favorite', dest='favorite', action='store', help="Number of favorite tasks to be displayed in the training mode", default=5)
    
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

def perform_training_task(task, favorite, user, db):
    print(task.FEN)
    print("\n")

    print("'Enter' - next task")
    if favorite:
        print("'f' - remove from favorites")
    else:
        print("'f' - add to favorites")
    print("'h' - hint")
    print("'s' - skip")
    print("'q' - quit")   
    print("\n")
    
    input = sys.stdin.readline()
    if input == 'h\n':
        print(task)
        print("\n")
        print("'Enter' - next task")
        if favorite:
            print("'f' - remove from favorites")
        else:
            print("'f' - add to favorites")
        print("'s' - skip")
        print("'q' - quit")   
        print("\n")
        input = sys.stdin.readline()
    
    if input == 'q\n':
        return sys.exit(0)
    elif input == 'f\n':
        if favorite:
            db.remove_from_favorites(user, task)
        else:
            db.add_to_favorites(user, task) 
    elif input == 's\n':
        return None
    elif input == '\n':
        db.update_training(user, task)
    
def perform_tasks(tasks, favorites, user, db):
    for task in tasks:
        perform_training_task(task, favorites, user, db)

def training(tasks, db_file, user, solved, new, favorite):
    try:
        db = ChessDb(db_file, tasks)
        
        print("First a few tasks that you already know")
        solved_tasks = favorite_tasks = new_tasks = []
        if solved > 0:
            solved_tasks = db.get_solved_tasks(user, solved, True)
        if favorite > 0:
            favorite_tasks = db.get_favorite_tasks(user, favorite, True)
        if new > 0:
            new_tasks = db.get_new_tasks(user, new)

        if len(solved_tasks) == 0 and solved > 0:
            print('No routine tasks found. Please do some tasks some.')
        else:
            # [print(task) for task in solved_tasks]
            perform_tasks(solved_tasks, False, user, db)
        
        print('----------------------------------------------')
        print("Next, some tasks that you liked exceptionally!")
        if len(favorite_tasks) == 0 and favorite > 0:
            print('No favorite tasks found. Please add some.')
        else:
            # [print(task) for task in favorite_tasks]
            perform_tasks(favorite_tasks, True, user, db)
        print('----------------------------------------------')
        print("And finally a few new tasks")
        if len(new_tasks) == 0 and new > 0:
            print('No new tasks found. You have done all excercises. Congratulations!')
        else:
            # [print(task) for task in new_tasks]
            perform_tasks(new_tasks, False, user, db)
            
        print('----------------------------------------------')
        
    except Error as e:
        print("Error in init_db")
        print(e)
        
def create_main_window():
    win = tkinter.Tk(screenName="Chess")
    win.mainloop()

def main():
    args = parse_args()
    tasks = parse_file(args['input'])
    db = ChessDb(args['db_file'], tasks)


    # create_main_window()

    if args['training']:
        training(tasks, args['db_file'], args['user'], int(args['solved']), int(args['new']), int(args['favorite']))
    else:
        tasks = filter_tasks(tasks, args)
        [print(task) for task in tasks]
        
    
if __name__ == '__main__':
    main()

