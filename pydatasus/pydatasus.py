#!/usr/bin/env python3

import platform
import re
import pathlib
from os import path, mkdir, remove, system
import argparse
import ftplib as ftp

from convert_dbf_to_csv import ReadDbf


class PyDatasus:

    def __init__(self):
        super().__init__()
        self.__none = None
        self.__page = ftp.FTP('ftp.datasus.gov.br')
        self.__page.login()
        self.__page.cwd('/dissemin/publicos/')
        if platform.system().lower() == "linux":
            self.__blast = path.join(path.dirname(__file__), './blast-dbf')
        elif platform.system().lower() == "windows":
            self.__blast = path.join(path.dirname(__file__),
                                     './blast-dbf.exe')
        self.__path_table = path.expanduser('~/datasus_tabelas/')
        self.__path_dbc = path.expanduser('~/datasus_dbc/')

    def get_table_csv(self, database: str, base: [str, list],
                      state: [str, list], date: [str, list]):

        date = self.__adjust_date(database, date)
        pattern = self.__generate_pattern(database, base, state, date)
        self.__create_folder(database, base, table_or_dbc='table')
        self.__table = open(f'{self.__path_table}{database}.csv', 'w+')
        self.__table.write('Endereço,Nome,Tamanho,Data\n')
        self.__get_data_table(database, pattern)
        self.__table.close()

    def get_file_dbc(self, database, base, state, date):
        date = self.__adjust_date(database, date)
        patterns = self.__generate_pattern(database, base, state, date)

        if isinstance(patterns, list):
            for pattern in patterns:
                self.__create_folder(database, pattern.split('\\')[0],
                                     table_or_dbc='dbc')
                self.__get_data_dbc(database)

        elif isinstance(patterns, str):
            self.__create_folder(database, patterns, table_or_dbc='dbc')
            self.__get_data_dbc(patterns)

    def get_data(self, database, base, state, date):
        self.get_table_csv(database, base, state, date)
        self.get_file_dbc(database, base, state, date)

    def __convert_dbc(self, db):
        if db.endswith('.csv'):
            pass

        elif db.endswith('.dbf'):
            pass

        else:
            after_ = db[:-3] + 'dbf'
            system(f'{self.__blast} {db} {after_}')
            remove(db)
            ReadDbf({after_}, convert='convert')
            remove(after_)
            after_ = None
            db = None

    def __adjust_date(self, database, dates):
        if database == 'SINAN':
            if isinstance(dates, str):
                return dates[2:4]
            elif isinstance(dates, list):
                return [date[2:4] for date in dates]
        elif database == 'SIHSUS':
            if isinstance(dates, str):
                return dates[2:4] + r'\d{2}'
            elif isinstance(dates, list):
                return [date[2:4] + r'\d{2}' for date in dates]
        else:
            return dates

    def __generate_pattern(self, database, base, states, dates):
        if base != 'DOFET':
            if isinstance(states, list) and isinstance(dates, list):
                return [ base + state + date + r'.[dDc][bBs][cCv]'
                         for state in states for date in dates ]
            elif isinstance(states, list) and isinstance(dates, str):
                return [ base + state + dates + r'.[dDc][bBs][cCv]'
                         for state in states ]
            elif isinstance(states, str) and isinstance(dates, str):
                return [ base + states + dates + r'.[dDc][bBs][cCv]' ]
            elif isinstance(states, str) and isinstance(dates, list):
                return [ base + states + date + r'.[dDc][bBs][cCv]'
                         for date in dates ]
        else:
            if isinstance(dates, list):
                return [
                    base + date[2:4] + r'.[dDc][bBs][cCv]' for date in dates
                ]
            elif isinstance(dates, str):
                return [
                    base + dates[2:4] + r'.[dDc][bBs][cCv]'
                ]

    def __create_folder(self, database, pattern, table_or_dbc):
        pathlib.Path(self.__path_table).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.__path_dbc).mkdir(parents=True, exist_ok=True)
        try:
            mkdir(self.__path_dbc + database + '/')
        except FileExistsError:
            pass

    def __get_data_table(self, database, pattern):
        branch = []

        self.__page.cwd(database)
        self.__page.dir(branch.append)

        r = re.compile('|'.join(pattern), re.IGNORECASE)

        for node in branch:
            if 'DIR' in node:
                self.__get_data_table(node.split()[3], pattern)
            elif re.match(r, node.split()[3]):
                self.__table.write('{},{},{} KB,{}\n'.format(
                                   self.__page.pwd(), node.split()[3],
                                   int(node.split()[2]) / 1000,
                                   node.split()[0])
                )
            else:
                pass

        self.__page.cwd('..')

    def __get_data_dbc(self, database):
        if path.isfile(self.__path_table + database + '.csv'):
            with open(self.__path_table + database + '.csv') as table:
                lines = table.readlines()
            for line in lines[1:]:
                self.__page.cwd(line.split(',')[0])
                if not path.isfile(self.__path_dbc + database + '/'
                                   + line.split(',')[1].split('.')[0]
                                   + '.csv'):

                    with open(self.__path_dbc + '/' + database + '/'
                              + line.split(',')[1], 'wb') as fp: 
                        self.__page.retrbinary('RETR ' + line.split(',')[1],
                                               fp.write)

                        self.__convert_dbc(self.__path_dbc + database + '/'
                                           + line.split(',')[1])
                else:
                    pass


if __name__ == '__main__':
    import struct
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--banco', required=True,
                    help='Banco de dados'
    )
    ap.add_argument('-b', '--base', required=True,
                    help='Base de dados'
    )
    ap.add_argument('-e', '--estado', required=True, 
                    help='Nome do estado ou sigla'
    )
    ap.add_argument('-a', '--ano', required=True, 
                    help='Lista contendo o ano que deseja baixar\
                            (aceita lista)'
    )
    args = vars(ap.parse_args())

    with open('database.json', 'r') as f:
        data = json.load(f)
        base = data[args['banco'].lower()][args['base'].lower()]

    with open('locales.json', 'r') as f:
        data = json.load(f)
        estado = data[args['estado'].lower()]

    datasus = PyDatasus()
    try:
        datasus.get_data(args['banco'].upper(), base, estado,
                         args['ano'].split(', ')
        )
    except struct.error:
        if platform.system().lower() == 'linux':
            system('clear')
            print("\n\nOps! Aconteceu algo inexperado. '_'\n") 
        elif platform.system().lower() == 'windows':
            system('cls')
            print("\n\nOps! Aconteceu algo inexperado. '_'\n") 
