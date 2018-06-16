#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import sys
import time
from datetime import timedelta, datetime


def choose_option():
    check_option = False
    print('[1] - Selecionar Projeto')
    print('[2] - Criar Projeto')
    print('----------------------------------------')

    while not check_option:
        try:
            option = int(input('\033[36m' + 'Escolha uma opção: \033[0m'))
            if option == 1:
                return show_projects()
            elif option == 2:
                return create_project()
            else:
                print('\033[31m' + '%s não é uma opção válida!' % option + '\033[0m')
        except ValueError as e:
            print('\033[31m' + '%s não é uma opção válida!' % e.args[0].split(': ')[1] + '\033[0m')


def create_project():
    print('----------------------------------------')
    name = input('Nome do Projeto: ')
    value = input('Valor da Hora: R$ ')
    hours = int(input('Total de Horas: '))
    print('----------------------------------------')

    minutes = hours * 60

    cursor.execute('''INSERT INTO project (name, hour_value, hours_total, remaining_minutes)
                      VALUES (?, ?, ?, ?)''', (name, value, hours, minutes))
    conn.commit()

    print('\033[32m' + '>>>>>>>>>>>>>>>>>>>>>>>>> Projeto Criado \033[0m')
    print('----------------------------------------')
    choose_option()


def show_projects():
    print('----------------------------------------')
    cursor.execute('SELECT project_id, name FROM project')
    result = cursor.fetchall()
    if len(result) > 0:
        for row in result:
            print('[{project_id}] - {name}'.format(project_id=row[0], name=row[1]))
        print('----------------------------------------')
        project_id = input('\033[36m' + 'Escolha um projeto: \033[0m')
        print('----------------------------------------')
        return select_project(project_id)
    else:
        print('\033[31m' + '>>>>>>>>>>>>>>>>>>> Não existem projetos \033[0m')
        print('----------------------------------------')
        choose_option()


def select_project(project_id):
    try:
        project_id = int(project_id)
        cursor.execute('SELECT name, hours_total, remaining_minutes, hour_value, start_project FROM project WHERE project_id=?', (project_id,))
        data = cursor.fetchone()

        remaining_hours = str(timedelta(minutes=data[2]))[:-3]
        total_money = data[1] * data[3]
        date = str_to_datetime(data[4])

        hours_total = add_zero_left(data[1])
        day = add_zero_left(date.day)
        month = add_zero_left(date.month)

        start_project = '{day}/{month}/{year}'.format(day=day, month=month, year=date.year)

        print('Projeto: %s' % data[0])
        print('Início do Projeto: %s' % start_project)
        print('Total de Horas: %s' % hours_total)
        print('Horas Restantes: %s' % remaining_hours)
        print('Total Recebido: ' + '\033[32m' + 'R$ %s,00 \033[0m' % total_money)
        print('----------------------------------------')
        print('\033[35m' + '  [1]-Voltar \033[0m' + '\033[33m' + ' [2]-Alterar \033[0m' + '\033[31m' + ' [3]-Remover \033[0m')
        print('\033[92m' + '  [4]-Start \033[0m' + '\033[91m' + '  [5]-Stop \033[0m' + '\033[94m' + '    [6]-Report \033[0m')
        print('----------------------------------------')
        return project_options(project_id)
    except ValueError as e:
        print('\033[31m' + '%s não é um projeto válido!' % e.args[0].split(': ')[1] + '\033[0m')
        return show_projects()
    except TypeError:
        print('\033[31m' + 'Projeto não encontrado! \033[0m')
        return show_projects()


def project_options(project_id):
    check_option = False
    while not check_option:
        try:
            option = int(input('\033[36m' + 'Escolha uma opção: \033[0m'))
            if option == 1:
                print('----------------------------------------')
                return choose_option()
            elif option == 2:
                return update_project(project_id)
                pass
            elif option == 3:
                return remove_project(project_id)
            elif option == 4:
                return start_job(project_id)
            elif option == 5:
                return finish_job(project_id)
            elif option == 6:
                return report(project_id)
            else:
                print('\033[31m' + '%s não é uma opção válida!' % option + '\033[0m')
        except ValueError as e:
            print('\033[31m' + '%s não é uma opção válida!' % e.args[0].split(': ')[1] + '\033[0m')


def remove_project(project_id):
    print('----------------------------------------')
    option = input('Tem Certeza? (S/N) ')
    if option.upper() == 'S':
        cursor.execute('DELETE FROM project WHERE project_id=?', (project_id,))
        conn.commit()
        print('----------------------------------------')
        print('\033[32m' + '>>>>>>>>>>>>>>>>>>>>>>> Projeto Removido \033[0m')
        print('----------------------------------------')
        return choose_option()
    else:
        print('----------------------------------------')
        return select_project(project_id)


def update_project(project_id):
    print('----------------------------------------')
    print('\033[33m' + ' [1]-Alterar Nome \033[0m' + '\033[32m' + '  [2]-Adicionar Horas \033[0m')
    print('----------------------------------------')
    check_option = False
    while not check_option:
        try:
            option = int(input('\033[36m' + 'Escolha uma opção: \033[0m'))
            if option == 1:
                print('----------------------------------------')
                name = input('Novo Nome: ')

                cursor.execute('UPDATE project SET name=? WHERE project_id=?', (name, project_id))
                conn.commit()

                print('----------------------------------------')
                print('\033[32m' + '>>>>>>>>>>>>>>>>>>>>>>>>>> Nome Alterado \033[0m')
                print('----------------------------------------')
                return select_project(project_id)
            elif option == 2:
                print('----------------------------------------')
                hours = int(input('Adicionar Horas: '))
                minutes = hours * 60

                cursor.execute('SELECT hours_total, remaining_minutes FROM project WHERE project_id=?', (project_id,))
                data = cursor.fetchone()

                hours += data[0]
                minutes += data[1]

                cursor.execute('UPDATE project SET hours_total=?, remaining_minutes=? WHERE project_id=?', (hours, minutes, project_id))
                conn.commit()

                print('----------------------------------------')
                print('\033[32m' + '>>>>>>>>>>>>>>>>>>>>>>> Horas Adicionada \033[0m')
                print('----------------------------------------')
                return select_project(project_id)
            else:
                print('\033[31m' + '%s não é uma opção válida!' % option + '\033[0m')
        except ValueError as e:
            print('\033[31m' + '%s não é uma opção válida!' % e.args[0].split(': ')[1] + '\033[0m')


def start_job(project_id):
    print('----------------------------------------')
    now_str = str_datetime_now()
    now_date = str_to_datetime(now_str)
    cursor.execute('''INSERT INTO project_job (start_job, project_id)
                      VALUES (?, ?)''', (now_str, project_id))
    conn.commit()
    for i in range(18):
        sys.stdout.write('\033[92m' + '\r%s>\033[0m' % ('>' * i))
        sys.stdout.flush()
        time.sleep(0.1)

    hour = add_zero_left(now_date.hour)
    minute = add_zero_left(now_date.minute)

    print('\033[92m' + ' Job iniciado às %s:%s \033[0m' % (hour, minute))
    print('----------------------------------------')
    return select_project(project_id)


def finish_job(project_id):
    print('----------------------------------------')
    comment = input('\033[33m' + 'O que foi feito?\033[0m' + ' ')
    print('----------------------------------------')
    cursor.execute('SELECT start_job FROM project_job WHERE project_id=? ORDER BY job_id DESC LIMIT 1', (project_id,))
    data = cursor.fetchone()

    start_job = data[0]
    start = str_to_datetime(start_job)
    now_str = str_datetime_now()
    now_date = str_to_datetime(now_str)

    elapsedTime = now_date - start
    minutes = divmod(elapsedTime.total_seconds(), 60)
    minutes = int(minutes[0])

    cursor.execute('SELECT remaining_minutes FROM project WHERE project_id=?', (project_id,))
    data = cursor.fetchone()

    remaining_minutes = data[0]
    remaining_minutes -= minutes

    cursor.execute('UPDATE project SET remaining_minutes=? WHERE project_id=?', (remaining_minutes, project_id))
    conn.commit()

    cursor.execute('UPDATE project_job SET finish_job=?, comment=? WHERE project_id=? ORDER BY job_id DESC LIMIT 1', (now_str, comment, project_id))
    conn.commit()
    for i in range(16):
        sys.stdout.write('\033[91m' + '\r%s>\033[0m' % ('>' * i))
        sys.stdout.flush()
        time.sleep(0.1)

    hour = add_zero_left(now_date.hour)
    minute = add_zero_left(now_date.minute)

    print('\033[91m' + ' Job finalizado às %s:%s \033[0m' % (hour, minute))
    print('----------------------------------------')
    return select_project(project_id)


def report(project_id):
    print('----------------------------------------')
    print('\033[37m' + '    Data do Job    | Duração |    Comentário \033[0m')
    print('----------------------------------------')
    cursor.execute('SELECT start_job, finish_job, comment FROM project_job WHERE project_id=?', (project_id,))
    data = cursor.fetchall()

    for row in data:
        start_date = str_to_datetime(row[0])
        finish_date = str_to_datetime(row[1])

        day = add_zero_left(start_date.day)
        month = add_zero_left(start_date.month)
        hour = add_zero_left(start_date.hour)
        minute = add_zero_left(start_date.minute)

        elapsedTime = finish_date - start_date
        minutes = divmod(elapsedTime.total_seconds(), 60)
        minutes = add_zero_left(int(minutes[0]))

        print('\033[37m' + '{day}/{month}/{year} - {hour}:{minute} | {minutes} min  | {comment} \033[0m'.format(day=day, month=month, year=start_date.year,
                                                                                                                hour=hour, minute=minute, minutes=minutes,
                                                                                                                comment=row[2]))
    print('----------------------------------------')
    return select_project(project_id)


def str_to_datetime(date):
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')


def str_datetime_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def add_zero_left(data):
    new_str = str(data)
    return new_str.zfill(2)


if __name__ == '__main__':
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')
    cursor.execute('''CREATE TABLE if not exists project (project_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, hours_total INT,
                      remaining_minutes INT, hour_value INT, start_project DATE DEFAULT (datetime('now','localtime')));''')
    cursor.execute('''CREATE TABLE if not exists project_job (job_id INTEGER PRIMARY KEY AUTOINCREMENT, start_job DATE, finish_job DATE,
                      comment TEXT, project_id INTEGER, CONSTRAINT fk_projects FOREIGN KEY (project_id) REFERENCES project(project_id) ON DELETE CASCADE);''')
    print('----------------------------------------')
    print('\033[33m' + '          CONTROLE DE PROJETOS\033[0m')
    print('----------------------------------------')
    choose_option()
    conn.close()
