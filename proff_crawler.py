# -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup as bsoup
import json

# x = {
#   "name": "Bounum",
#   "Aksjer": 30,
#   "Prosent": 100,
#   "owners":[
#       { 
#           "name": "Something",
#           "Aksjer": 30,
#           "Prosent": 100,
#           "owners": [
#               { 
#                   "name": "Something else",
#                   "Aksjer": 30,
#                   "Prosent": 100,
#                   "owners": []
#               },
#               { 
#                   "name": "Something",
#                   "Aksjer": 30,
#                   "Prosent": 100,
#                   "owners": []
#               }
#               ]
#       },
#       { 
#           "name": "Something else",
#           "Aksjer": 30,
#           "Prosent": 100,
#           "owners": []
#       },
#       { 
#           "name": "Something",
#           "Aksjer": 30,
#           "Prosent": 100,
#           "owners": []
#       }
#       ]
# }

# y = json.dumps(x, indent=4)
# print(y)


def remove_whitespace(string):
    """
    Remove whitespace in string
    """
    return  string.strip().replace(' ', '')


def get_html(url):
    """
    Fetches html from a given url
    """
    r = requests.get(url).text
    return r

def prepend_domain(link):
    """
    Urls are directly combined as given in *args
    """
    top_level_domain ='https://www.proff.no'
    return top_level_domain + link 

class ProffCrawler:
    def __init__(self, company_name):
        top_level_domain ='https://www.proff.no'
        search_url = (f'{top_level_domain}/bransjes%C3%B8k?q='
                      f'{remove_whitespace(company_name)}')
        shareholders_url = self.get_shareholders_url(search_url, company_name)
        shareholders = self.get_json(shareholders_url)
        concern = shareholders['entity']
        owners = shareholders['owners']
        concern['owners'] = owners

        self.concern = concern

    def get_shareholders_url(self, url, company_name):
        search_html = get_html(url)
        company_url = self.get_hyperlinks(search_html, company_name)
        company_url = prepend_domain(company_url)
        company_html = get_html(company_url)
        shareholders_url = self.get_hyperlinks(company_html, 'Vis alle aksjonærer')
        shareholders_url = prepend_domain(shareholders_url)
        return shareholders_url

    def get_hyperlinks(self, html, search_word):
        soup = bsoup(html, 'html.parser').find(string=search_word)
        try:
            return soup.find_parent('a')['href']
        except AttributeError:
            return ''

    def get_json(self, url=None):
        html = get_html(url)
        soup = bsoup(html, 'html.parser')
        shareholders = soup.find(id='share-holders') #Find javascript share-holders
        shareholders = shareholders.script.get_text() #Get script part
        shareholders = shareholders.strip() #Strip excess whitespace
        shareholders = shareholders.split('\n')[0] #Only use first variable (shareholders)
        shareholders = shareholders.split(' = ')[1] #Remove variablename
        shareholders = shareholders.strip(';\r') #Remove carriage return
        shareholders = json.loads(shareholders)
        return shareholders

    def collect_data(self, concern):
        has_owners = 'owners' in concern
        is_company = owner['company']
        if has_owners and is_company:
            owners = concern['owners']

        
        else:
            return break


        for owner in owners:

            print(owner)
            self.collect_data(owner)
        # for owner in owner_dict:
        #     if not has_owners:
        #         break

        #     else:
        #         collect_data(owner)
            # print(company)
            # print(owner['owner'])
            # items = owner.items()
            # print(items)
            # if 'owner' not owner.keys() and 'ent:

            # print(c)
            # print(owner)
            # owner['hei'] = 'hei'
            # print(owner)
        # print(concern)
            # owner.update('hei')
            # print(owner)

        # print(self.concern)


    # def crawl(self, default=True):
    #     shareholders_url = self.crawl_to_shareholders()
    #     data = self.collect_data(pd.DataFrame(), shareholders_url, self.company_name)
    #     N = len(data['Navn'])
    #     if default:
    #         while np.any(data['Traversed'] == False):
    #             for index, row in data.iterrows():
    #                 data.loc[index, 'Traversed'] = True
    #                 if row['Bedrift'] and not row['Traversed']:
    #                     url = self.concatenate_urls(self.TLD, row['Url'])
    #                     new_data = self.collect_data(pd.DataFrame(), url, row['Bedriftslinje'])
    #                     data = data.append(new_data, ignore_index=True)
    #     return data
    def blah(self):
        d.update(bedrift)

if __name__ == '__main__':
    company_name = 'Bonum AS'
    # company_name = 'Femstø AS'
    # company_name = 'Rec Silicon ASA'
    # company_name = quote('Femstø AS')
    instance  = ProffCrawler(company_name)
    concern = instance.concern
    instance.collect_data(concern)
    # instance.collect_data()
    # instance.main()
    #            'Aksjetype', 'Antall Aksjer',
    #            'Aksjeprosent', 'Totale Aksjer'] #Dataframe columns to collect
    # data = instance.crawl()
    # data[columns].to_csv('shareholders.csv', index=False)
