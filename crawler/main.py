#!/home/webuser/pyvenv/bin/python
# -*- coding:utf-8 -*-

# loading default config
import sys
sys.path.append("/home/webuser/daan-3hr-weather-forecast/config")
from default import *


import requests
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd


# crawl data into dataframe (Lab2)
def spider_report(d_code):
    url = 'http://www.cwb.gov.tw/V7/forecast/town368/3Hr/'  + d_code + '.htm'
    print("spider is crawling %s..." % url)

    try:
        req = requests.get(url)
    except:
        print('WARNING: url fetching error, please try again and check district code...')
        sys.exit()

    if req.status_code != 200:
        print('WARNING: http status code returns %d...' % req.status_code)
        sys.exit()

    req.encoding = 'utf-8' # 不指定會發生編碼錯誤
    soup = BeautifulSoup(req.text, 'html.parser')
    trs = soup.find_all('tr')
    print("    fetching data from completed, parsing...")
    
    columns = ['record_t', # 0
               'weekday', # 1
               'wx', # 2
               't', # 3 
               'at', # 4
               'beaufort', # 5
               'wind_dir', # 6
               'rh', # 7
               'pop', #8 
               'ci'] # 9
    df = pd.DataFrame(columns=columns)
    print("    building empty dataframe, there're %d columns in dataframe" % len(columns))

    year_s = []
    year_s.append("%d" % datetime.datetime.now().year)
    year_s.append("%d" % (datetime.datetime.now() + datetime.timedelta(days=1)).year) # in case tmrr is next year
    year_s.append("%d" % (datetime.datetime.now() + datetime.timedelta(days=2)).year) # in case it's next year in 2 days
    colspans = []
    dates = []
    days = []
    k = 0
    for idx, td in enumerate(trs[0].findAll('td')): # trs[0] 是時間相關的列
        if idx > 0:
            if td.has_attr('colspan'):
                colspans.append(td.attrs['colspan'])
            else:
                colspans.append("1")
            days.append(re.findall('[一|二|三|四|五|六|日]', td.text)[0]) # 用正規表示式把星期"幾"選出來
            month_n_date = re.findall('\d+', td.text)
            dates.append(year_s[k] + '-' + month_n_date[0] + '-' + month_n_date[1])
            k+=1
    print("    cleaned up time information...")
    
    # insert data into dataframe
    record_ts = []
    weekdays = []
    hours = trs[1].findAll('span')
    k = 0
    for i in range(0, len(colspans)):
        for j in range(0, int(colspans[i])):
            record_ts.append(dates[i] + ' ' + hours[k].text)
            k+=1
            weekdays.append(days[i])
    df['record_t'] = record_ts #0
    df['weekday'] = weekdays #1
    
    wxs = []
    for img in trs[2].findAll('img'):
        wxs.append(img.attrs['alt'])
    df['wx'] = wxs #2
    print("    %d:%d columns data inserted..." % (0,2))
    
    vals = []
    for i in range(3, 10):
        if i is not 8: # 降雨機率可能要展開 colspan == 2
            tds = trs[i].findAll('td')
            for idx, td in enumerate(tds):
                if idx > 0:
                    vals.append(td.text)
            df.iloc[:,i] = vals
            vals = []
    print("    %d:%d columns data inserted...except %d" % (3, 9, 8))
    
    pops = [] # probability of precipitation
    rep = 0
    for idx, td in enumerate(trs[8].findAll('td')):
        if idx > 0:
            if td.has_attr('colspan'):
                rep = int(td.attrs['colspan'])
            else:
                rep = 1
            for i in range(0, rep):
                pops.append(td.text)
    df['pop'] = pops
    print("    inserted the %dth column" % 8)
    df.insert(0, 'station_sid', int(d_code))
    print("    inserted the district code: %s at the beginning column" % d_code)
    print("crawling completed, return dataframe\n")
    return df

from sqlalchemy import DateTime, TIMESTAMP, text, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import create_engine
engine_para = ('mysql+mysqldb://' + 
                MYSQL_CONFIG['user'] + ':' +
                MYSQL_CONFIG['passwd'] + '@' +
                MYSQL_CONFIG['host'] + ':3306/' +
                MYSQL_CONFIG['db'] + '?charset=' +
                MYSQL_CONFIG['charset'])
engine = create_engine(engine_para, max_overflow=5)

class Report(Base):
    __tablename__ = 'report'
    rid = Column(Integer, primary_key=True)
    #station_sid = Column(Integer, ForeignKey('station.sid'))
    station_sid = Column(Integer)
    update_t = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    record_t = Column(DateTime)
    weekday = Column(String(3))
    wx = Column(String(32))
    t = Column(Integer)
    at = Column(Integer)
    beaufort = Column(String(16))
    wind_dir = Column(String(3))
    rh = Column(String(4))
    pop = Column(String(4))
    ci = Column(String(8))

def recreate_table_report():
    if engine.dialect.has_table(engine, 'report'):
        Base.metadata.tables['report'].drop(engine)
        print('table report has been droped')
    Base.metadata.tables['report'].create(engine)
    print('table report has been created...')
    
def insert_df_into_mysql(df):
    Session = sessionmaker(bind=engine)
    session = Session()
    df.to_sql(name='report', con=engine, if_exists='append', index=False)
    session.close()

def autosave_df_to_csv(df):
    outfile_csv = datetime.datetime.now().strftime("%Y%m%d%H%m%S_dataframe.csv")
    df.to_csv(outfile_csv, sep=',', encoding='utf-8', index=False)
    print('csv file %s saved\n' % outfile_csv)
    
if __name__ == '__main__':
    #recreate_table_report()
    df = spider_report('6300300')
    autosave_df_to_csv(df)
    #insert_df_into_mysql(df)
    #infile_csv = '20170823170800_dataframe.csv'
    #df = pd.read_csv(infile_csv, sep=',')
    
    

