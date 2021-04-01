#!/usr/bin/env python3

import platform
import re
import pathlib
import tempfile
from os import path, mkdir, remove, system
import argparse
import ftplib as ftp
import pandas as pd

from pydatasus.convert_dbf_to_csv import ReadDbf


class start:

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
        self.__path_table = tempfile.TemporaryDirectory(dir='/tmp/')
        self.__path_dbc = tempfile.TemporaryDirectory(dir='/tmp/')
        self.__list_df = []

    def get_table_csv(self, database: str, base: [str, list],
                      state: [str, list], date: [str, list]):

        date = self.__adjust_date(database, date)
        pattern = self.__generate_pattern(database, base, state, date)
        # self.__create_folder(database, base, table_or_dbc='table')
        self.__table = open(f'{self.__path_table.name}{database}.csv', 'w+')
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
                return self.__get_data_dbc(database)

        elif isinstance(patterns, str):
            self.__create_folder(database, patterns, table_or_dbc='dbc')
            return self.__get_data_dbc(patterns)

    def get_data(self, database, base, state, date):
        self.get_table_csv(database, base, state, date)
        return self.get_file_dbc(database, base, state, date)

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
            return pd.read_csv(after_[:-3]+'csv')

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
        # pathlib.Path(self.__path_table).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.__path_dbc.name).mkdir(parents=True, exist_ok=True)
        try:
            mkdir(self.__path_dbc.name + '/' + database + '/')
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
        if path.isfile(self.__path_table.name + database + '.csv'):
            with open(self.__path_table.name + database + '.csv') as table:
                lines = table.readlines()
            for line in lines[1:]:
                self.__page.cwd(line.split(',')[0])
                if not path.isfile(self.__path_dbc.name + '/' + database + '/'
                                   + line.split(',')[1].split('.')[0]
                                   + '.csv'):

                    with open(self.__path_dbc.name + '/' + '/' + database + '/'
                              + line.split(',')[1], 'wb') as fp: 
                        self.__page.retrbinary('RETR ' + line.split(',')[1],
                                               fp.write)

                        self.__list_df.append(
                            self.__convert_dbc(self.__path_dbc.name + '/'
                                               + database + '/'
                                               + line.split(',')[1])
                        )
                else:
                    pass

            return pd.concat(self.__list_df)

        self.__page.close()

