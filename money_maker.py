#!/usr/bin/python
# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import urllib.request, sys, pickle

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class Company:
    
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.financial_results = []
    
    def info(self):
        return ('Nazwa: ' + self.name) + "\n" + ('LINK: '+ str(self.link)) + "\n" + "\n" + str(self.financial_results) + "\n" + "\n"

    def download(self):
        try:
            source = urllib.request.urlopen(self.link).read()
            soup = BeautifulSoup(source,'html.parser')
            tables = soup.find_all('table')
            table_rows = tables[0].find_all('tr')
            for tr in table_rows:
                x = []
                table_column = tr.find_all('td')
                for td in table_column:
                    data = str(td)
                    # print(data)
                    if (data[4:20]=='class="last-day"') : x.append(data[22:32])
                    elif (data[4:22]=='class="payout-day"') : x.append(data[24:34])
                    elif (data.find('%</td>'))!=-1: x.append(str(data[5:(data.find('%'))]))
                    elif (data.find(' zł'))!=-1: x.append(str(data[5:(data.find(' zł'))]))
                    else : x.append(str(data[5:-5]))
                self.financial_results.append(list(x))
            self.financial_results.pop(0)

        except Exception as e: 
            print("Nie można pobrać danych o spółce " + str(self.name) + ". Błąd: " + str(e))
            print(self.link)

    def filtr(self, amounts):
        self.years_dict = {}
        self.years_list = [] 
        for x in self.financial_results:
            if x[0] not in self.years_dict:  self.years_dict[x[0]] = 0
            if x[0] not in self.years_list:  self.years_list.append(x[0])
            for y in self.years_dict:
                if (x[0])==(y): 
                    self.years_dict[y]= self.years_dict[y] + float(x[4])
        
        if (len(self.years_list)) > 4:
            amounts[0] = amounts[0] + 1
            if filtr_years_in_a_row(self.years_list,4):
                amounts[1] = amounts[1] + 1
                if filtr_increasing_divid(self.years_list, self.years_dict):
                    amounts[2] = amounts[2] + 1
                    best_companies.append(self)




def save_to_file(objects):
    with open(data_file, 'wb') as f:
        pickle.dump(objects,f)

def read_from_file():
    try:
        with open(data_file, 'rb') as f:
            return pickle.load(f)

    except FileNotFoundError:
        print('Cannot find database')
        objects = []
        return objects

def update_companies_list():
    companies_list = []
    source = urllib.request.urlopen(link).read()
    soup = BeautifulSoup(source,'html.parser')
    tables = soup.find_all('table')
    table_rows = tables[0].find_all('tr')
    for tr in table_rows:
        x = []
        table_column = tr.find_all('td')
        for td in table_column:
            data = str(td)
            # print(data[74:-18])
            if (data[35:56]=='field-instrument-name') : x.append(data[59:-5])
            elif (data[35:50]=='last-day active') : x.append(data[53:-5])
            elif (data[35:39]=='yeld'): x.append(str(data[60:-6]))
            elif (data[35:43]=='dividend'): x.append(str(data[64:-8])) #64:-8
            elif (data[35:45]=='payout-day'): x.append(data[56:-5])
            elif (data[35:62]=='field-instrument-short-name'): x.append(data[74:(data.find('/dywidendy">')+10)])
        companies_list.append(list(x))
    companies_list.pop(0)

    print("Pobrano " + str(len(companies_list)) + " firm")
    return companies_list


def fill_objects():
    objects = []
    objects = read_from_file()

    if not len(objects):
        print('Downloading data...')
        companies_list = update_companies_list()
        for i in companies_list:
        # for i in companies_list[7:8]:
            index = int(companies_list.index(i))
            print ((str(index+1) + '/' + str(len(companies_list))) + ' (' + str(int(((index+1)/len(companies_list))*100)) + '%)')
            bufor = Company(companies_list[index][1], 'https://strefainwestorow.pl' + companies_list[index][0])
            bufor.download()
            objects.append(bufor)

        save_to_file(objects)
        print('Saved to file')
    return objects

def filtr_years_in_a_row(years_list, amount):
    for i in range(amount-1):
        if int(years_list[i])-int(years_list[i+1]) != 1:
            return 0
    return 1

def filtr_increasing_divid(years_list, years_dict):
    divid = 100000
    for i in years_list:
        if (float(years_dict[i]) > divid):
            return 0
        divid = float(years_dict[i])
    return 1

def delta_divid(objects):
    return (float(objects.financial_results[0][4])-float(objects.financial_results[1][4]))/float(objects.financial_results[1][4])



def update_years_list():
    years = []
    source = urllib.request.urlopen(link).read()
    soup = BeautifulSoup(source,'html.parser')
    tables = soup.find("ul", {"class": "nav nav-pills"})
    table_rows = tables.find_all('li')
    for tr in table_rows:
        table_column = tr.find_all('a')
        for td in table_column:
            data = str(td)
            # print(data)
            if (data[0:40]=='<a href="/dane/dywidendy/lista-dywidend/') : years.append(data[40:44])
    return years



link = "https://strefainwestorow.pl/dane/dywidendy/lista-dywidend/1993"
years_list = update_years_list()
print(bcolors.WARNING + "Dane dostepne dla nastepujących lat:" + bcolors.ENDC + bcolors.BOLD)
for i in reversed(years_list):
    print(bcolors.BOLD + i + bcolors.ENDC)


choosed_year = input(bcolors.WARNING + "Który rok chcesz przeanalizować? " + bcolors.ENDC)
while (choosed_year not in years_list):
    choosed_year = input(bcolors.WARNING + "Wybierz rok z listy: " + bcolors.ENDC + bcolors.BOLD)

link = "https://strefainwestorow.pl/dane/dywidendy/lista-dywidend/"+str(choosed_year)

data_file = choosed_year + '.dat'
objects = fill_objects()

amounts = [0,0,0]
best_companies = []

for i in objects: i.filtr(amounts)
  
print(bcolors.OKGREEN + "Sprawdzonych spółek: " + bcolors.WARNING + str(len(objects)) + bcolors.ENDC)
print(bcolors.OKGREEN + "Spółek z dywidendą ponad 4 lata: " + bcolors.WARNING + str(amounts[0]) + bcolors.ENDC)
print(bcolors.OKGREEN + "Spółek z dywidendą ponad 4 lata z rzedu: " + bcolors.WARNING + str(amounts[1]) + bcolors.ENDC)
print(bcolors.OKGREEN + "Spółek z rosnaca dywidenda: " + bcolors.WARNING + str(amounts[2]) + bcolors.ENDC + '\n')

best_companies.sort(key=delta_divid, reverse=True)
for i in best_companies:
    print(str(best_companies.index(i)+1) + '. ' + bcolors.BOLD + i.name + bcolors.ENDC + ' wzrost o ' + bcolors.OKGREEN + str(int(delta_divid(i)*100)) + '%' +bcolors.ENDC)
    print(bcolors.HEADER + i.link + bcolors.ENDC + '\n')