# -*- coding: utf-8 -*-
import certifi
import re
import json
import pandas as pd
import numpy as np
import urllib3 as url3
from bs4 import BeautifulSoup as bs
from urllib.parse import quote

class ProffCrawler:
    def __init__(self, company_name, TLD ='https://www.proff.no'):
        ###
        #Defining starting variabels#
        ###
        bransje_url = 'https://www.proff.no/bransjes%C3%B8k?q={}'.format(self.rw(company_name))
        self.bransje_url = bransje_url 
        self.TLD = TLD
        self.company_name = company_name


    def rw(self, url_name):
        """
        Remove whitespace in url
        """
        return  url_name.strip().replace(' ', '')

    def concatenate_urls(self, *args):
        """
        Urls are directly combined as given in *args
        """
        return ''.join(args)

    def get_roller(self, url):
        return url.replace('selskap', 'roller')

    def get_html(self, url_name):
        """
        Fetches html from a given url
        """
        user_agent = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        http = url3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(), headers=user_agent)
        r = http.request('GET', url_name)
        return r.data

    def get_hyperlinks(self, html, search_word):
        soup = bs(html, 'lxml').find(string=search_word)
        try:
            return soup.find_parent('a')['href']
        except AttributeError:
            return ''

    def show_all_shareholders(self, html):
        soup = bs(html, 'lxml').find(string='Vis alle aksjonærer')
        try:
            return soup.find_parent('a')['href']
        except AttributeError:
            return ''

    def get_title(self, html, ):
        soup = bs(html, 'lxml')
        return soup.title.string
     
    def crawl_to_shareholders(self):
        """
        Crawling to the sharholderspage of the parent company
        defined in company_name
        """
        html_company = self.get_html(self.bransje_url) #Initial html of search page
        hyperlinks = self.get_hyperlinks(html_company,self.company_name) #Find url matching company name
        company_url = self.concatenate_urls(self.TLD, hyperlinks) # Attach url to TLD
        company_url = self.get_roller(company_url) #Crawl directly to "roller"-page
        html_roller = self.get_html(company_url) #Get html of roller-page
        shareholders_url = self.show_all_shareholders(html_roller) #Find shareholders url
        shareholders_url = self.concatenate_urls(self.TLD, shareholders_url) #Crawl to shareholders-page
        print(shareholders_url)
        return shareholders_url

    def collect_data(self, dataframe, url, path):
        html = self.get_html(url)
        pattern = b"var shareholdersData = JSON.parse\((.+)\);" 
        pat = re.compile(pattern)
        shareholders_data = pat.findall(html)[0] #Find Json data
        shareholders_data = json.loads(json.loads(shareholders_data))#Convert to dict
       
        sdo = shareholders_data['owners'] 
        N = len(shareholders_data['owners'])

        columns = ['Bedriftslinje', 'Navn', 'Bedrift',
                   'Aksjetype', 'Antall Aksjer',
                   'Aksjeprosent', 'Totale Aksjer',
                   'Url', 'Traversed'] #Dataframe columns to collect

        data = [] 
        for i in range(N):
            name = sdo[i]['name']
            company_trail = path + '\n' + name  
            shareType = sdo[i]['shareType']
            totalShares = sdo[i]['totalShares']
            numberOfShares = sdo[i]['numberOfShares']
            sharePercentage = sdo[i]['sharePercentage']
            tabUrl = quote(sdo[i]['tabUrl'])
            company = sdo[i]['company']
            traversed = False
            data.append([company_trail, name, company,
                        shareType, numberOfShares,
                        sharePercentage, totalShares,
                        tabUrl, traversed])

        data = pd.DataFrame(data,columns=columns)
        data['Bedrift'] = data['Bedrift'].astype(bool)
        dataframe = dataframe.append(data, ignore_index=True)
        print(dataframe)
        return dataframe 

    def crawl(self, default=True):
        shareholders_url = self.crawl_to_shareholders()
        data = self.collect_data(pd.DataFrame(), shareholders_url, self.company_name)
        N = len(data['Navn'])
        if default:
            while np.any(data['Traversed'] == False):
                for index, row in data.iterrows():
                    data.loc[index, 'Traversed'] = True
                    if row['Bedrift'] and not row['Traversed']:
                        url = self.concatenate_urls(self.TLD, row['Url'])
                        new_data = self.collect_data(pd.DataFrame(), url, row['Bedriftslinje'])
                        data = data.append(new_data, ignore_index=True)
        return data

if __name__ == '__main__':
    company_name = 'Bonum AS'
    company_name = 'Rec Silicon ASA'
    # company_name = quote('Femstø AS')
    
    instance  = ProffCrawler(company_name)

    columns = ['Bedriftslinje', 'Navn', 
               'Aksjetype', 'Antall Aksjer',
               'Aksjeprosent', 'Totale Aksjer'] #Dataframe columns to collect
    data = instance.crawl()
    # data[columns].to_csv('shareholders.csv', index=False)
