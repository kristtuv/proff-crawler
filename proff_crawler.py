# -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup as bsoup
import json
from collections import OrderedDict

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
        del concern['owners']
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
        is_company = concern['company']
        if has_owners and is_company:
            owners = concern['owners']
            for owner in owners:
                url = prepend_domain(owner['tabUrl'])
                shareholders = self.get_json(url)
                owner['owners'] = shareholders['owners']
                self.collect_data(owner)

    def extract_desired_data(self):
        ['name', 'organisationNumber', 'totalShares',
         'location', 'numberOfShares', 'sharePercentage', 'owners']

    def __str__(self):
        return json.dumps(self.concern, indent=4)


if __name__ == '__main__':
    company_name = 'Bonum AS'
    # company_name = 'Femstø AS'
    # company_name = 'Rec Silicon ASA'
    instance  = ProffCrawler(company_name)
    concern = instance.concern
    # print(type(concern))
    instance.collect_data(concern)
    print(instance)
