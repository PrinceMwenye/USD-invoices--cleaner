#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 15:31:05 2020

@author: prince
"""


import pandas as pd
import numpy as np
inv = pd.read_csv('trial.csv')
exchanges = pd.read_csv('exchangeusd.csv')
import re
inv = inv[inv['Invoice'].notnull()]


def cleaner(row):
    if str(row['Invoice'])[0:3] == 'IN0':
        return 'good'
    elif str(row['Invoice']) == 'Reference:':
        return 'good'
    else:
        return 'bad'
    
inv['type'] = 0

inv['type'] = inv.apply(lambda row: cleaner(row), axis = 1)    
    
inv = inv[inv['type'] == 'good']    
inv = inv.iloc[:, [0,1,2,3,4,5,6,7,8,9,10]]

inv['Type'] = 0

def cleaner_2(row):
    if str(row['Invoice']) == 'Reference:':
        row['Type'] = row['Posting Date']
        return row['Type']
    
    
inv['Type'] = inv.apply(lambda row: cleaner_2(row), axis = 1)   


new_column = inv['Type'].reset_index()
inv = inv[inv['Invoice'] != 'Reference:']

new_column['Type'] = new_column['Type'].map(lambda i: str(i))

new_column = new_column[new_column['Type'] != 'None']
inv.drop(['Type', 'Ship Date'], inplace = True, axis =1 )
inv = inv.reset_index()
inv.drop(['index'], axis = 1, inplace = True)
new_column.drop(['index'], axis = 1, inplace = True)

new_column = new_column.reset_index()

inv = pd.concat([inv, new_column], axis = 1)

serp = lambda i: str(i[7:]) if i[:2] == 'IN' else str(i[9:])

inv['Invoice'] = inv['Invoice'].map(serp)

inv = inv.iloc[:, [0,1,6,8,9,11]]

inv['Type'] = inv['Type'].astype('string')


cleaner = lambda k: float(re.sub(',','', str(k))) 
inv[['Year', 'Prd.']] = inv[['Year', 'Prd.']].applymap(cleaner)

no_description = inv[inv['Type'] == 'nan']

def usd(row):
    if 'usd' in str(row['Type']).lower() or 'dpo' in str(row['Type']).lower() or 'nostro' in str(row['Type']).lower() :
        return 'USD'
    elif str(row['Type']) == 'nan':
        return 'unkown'
    else:
        return 'RTGS'

inv['Currency'] = 0

inv['Currency'] = inv.apply(lambda row: usd(row), axis = 1)


usd_invoices = inv[inv['Currency'] == 'USD']

usd_invoices['rate'] = 0


import re
def interbank(row):
    if '1:1' in str(row['Type']).lower():
        return 1
    else:
        try:
            return float(re.findall('8....|$', row['Type'])[0]) #|$ gives you an extra '' so you can split by first elemnt of list
        except:
            return 1
     
        
           
    

usd_invoices['rate'] = usd_invoices.apply(lambda row: interbank(row), axis = 1)

usd_invoices['Income'] = round((usd_invoices['Year'] / usd_invoices['rate']),1)
usd_invoices['exchange_diff'] = usd_invoices['Year'] - usd_invoices['Income']

usd_invoices = usd_invoices.sort_values('exchange_diff', ascending = False)


usd_invoices['Actual'] = usd_invoices['Actual'].map(lambda i: i.split()[0])

usd_invoices.columns = ['Inv_num', 'Acc_num', 'Date', 'Acc_pac amount', 'ac', 'Description', 'Currency', 'interbank_rate', 'USD_income', 'exchange_diff']

usd_invoices.drop(['ac'], inplace = True, axis = 1)
usd_invoices.to_csv('feb1.csv', index = False)

exchanges = pd.concat([exchanges, usd_invoices], axis = 0)

exchanges = exchanges.drop_duplicates()
exchanges.to_csv('exchangeusd.csv', index = False)


no_description.to_csv('no_dep.csv', index = False)








	
    