#coding=utf-8
"""
author:omzsl
desc:read chrome history and generate a analysis report
python version:3.6
"""
"""
tips:
* close chrome browser before you run the script
* 
"""
import os
import sqlite3
import pandas as pd
import operator
from collections import OrderedDict
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from reportlab.pdfgen import canvas #reference:https://www.reportlab.com/docs/reportlab-userguide.pdf
from reportlab.lib.units import inch 
from reportlab.lib.utils import ImageReader
import image
import io 
import jieba#中文分词 
import chrometime
import url 


#generate word cloud
#input string output png image object
def get_word_cloud(s):
    #vera font is used to fix wordcloud's chinese bug
    srch_keyword_cloud = WordCloud(background_color="white",font_path =r'Vera.ttf',width=1000, height=860, margin=2).generate(s)
    fig = plt.figure(figsize=(10, 10))
    plt.imshow(srch_keyword_cloud)
    plt.axis("off")
    #plt.show()
    imgdata = io.BytesIO()
    fig.savefig(imgdata, format='png')
    imgdata.seek(0)  # rewind the data
    plt.gcf().clear()
    plt.close()  # clear previos plot
    return ImageReader(imgdata)



    

# generate pdf using the data we get
# abandoned
def pdf_produce(image0):
    report=canvas.Canvas("HelloMyHistory.pdf")  
    report.drawString(1*inch, 10.5*inch, "your search keywords' wordcloud:")
    report.drawImage(image0, 0, 2*inch, 9*inch, 9*inch)
    report.showPage()                           
    report.save()     




if __name__ == '__main__':
###########################initialize################################################################################
    #path to user's history database (Windows Chrome)
    data_path = os.path.expanduser('~')+r"\AppData\Local\Google\Chrome\User Data\Default"
    files = os.listdir(data_path)
    #history_db = os.path.join(data_path, 'history')
    history_db = 'history'
    #establish connection
    c = sqlite3.connect(history_db)
    # create new report file
    report=canvas.Canvas("HelloMyHistory.pdf")
    #define your own query here 
    select_statement = "SELECT urls.url urls.visit_count FROM urls, visits WHERE urls.id = visits.url;"

#####################search keyword analysis###############################################################
    srch_keyword = "SELECT lower_term from keyword_search_terms"
    srch_keyword_resullt = pd.read_sql_query(srch_keyword, c)
    report.drawString(1*inch, 10.5*inch, "your search keywords' wordcloud:")
    report.drawImage(get_word_cloud(" ".join(list(srch_keyword_resullt['lower_term']))), 0, 2*inch, 9*inch, 9*inch)#word cloud pic insert into pdf
    report.showPage()# the showPage() method will end this page and new data will show in next page

######################websites keyword analysis#################################################################
    title_keyword = "SELECT title FROM urls;"
    title_keyword_result = pd.read_sql_query(title_keyword,c)
    divided_result = ""
    for line in title_keyword_result['title']:
        divided_result += " ".join(jieba.cut(line)) + " "
    report.drawString(1*inch, 10.5*inch, "your title' wordcloud:")
    report.drawImage(get_word_cloud(divided_result), 0, 2*inch, 9*inch, 9*inch)#word cloud pic insert into pdf
    report.showPage() 

##########################view duration analysis#################################################################### 
    view_duration = "SELECT urls.url,visits.visit_duration,visits.visit_time from urls, visits WHERE urls.id = visits.url ORDER BY visits.visit_duration DESC;"
    view_duration_result = pd.read_sql_query(view_duration,c)
    first_site = view_duration_result.iloc[0]
    report.drawString(1*inch, 10.5*inch, str(chrometime.date_from_chrome(first_site['visit_time']))+" you stay in : ")
    report.drawString(1*inch, 10*inch, first_site['url'])
    report.drawString(1*inch, 9.5*inch, str(chrometime.chrome_time_diff(first_site['visit_duration'])+" minutes."))
    ## domain visit cnt 
    view_duration_result['domain'] = view_duration_result['url'].apply(url.get_url_netloc)
    view_duration_result['duration'] = view_duration_result['visit_duration'].apply(lambda x :round(int(chrometime.chrome_time_diff(x))/60,1))
    domian_duration = view_duration_result.groupby('domain').duration.sum().sort_values(ascending=False)[:40]
    #print(list(domian_duration.values))
    fig = plt.figure(figsize=(10, 10))
    plt.bar(range(20), list(domian_duration.values), align='edge')
    plt.xticks(rotation=45)
    plt.xticks(range(20), domian_duration.index)
    plt.title("网站停留时间前20")
    #plt.show()
    imgdata = io.BytesIO()
    fig.savefig(imgdata, format='png')
    imgdata.seek(0)  # rewind the data
    report.drawImage(ImageReader(imgdata), 0, 0, 9*inch, 9*inch)
    plt.gcf().clear()
    plt.close()  # clear previos plot
    report.showPage()

    domian_duration = view_duration_result.groupby('domain').count().visit_time.sort_values(ascending=False)[:40]
    #print(list(domian_duration.values))
    fig = plt.figure(figsize=(10, 10))
    plt.bar(range(20), list(domian_duration.values), align='edge')
    plt.xticks(rotation=45)
    plt.xticks(range(20), domian_duration.index)
    plt.title("网站点击次数前20")
    #plt.show()
    imgdata = io.BytesIO()
    fig.savefig(imgdata, format='png')
    imgdata.seek(0)  # rewind the data
    report.drawImage(ImageReader(imgdata), 0, 0, 9*inch, 9*inch)
    plt.gcf().clear()
    plt.close()  # clear previos plot
    report.showPage()


    report.save()
