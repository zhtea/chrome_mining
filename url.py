#coding=utf-8
"""
author:omzsl
"""
#from urllib.parse import urlsplit 
import tldextract


# use url.parse.urlsplit to parse url and return main domain 
def get_url_netloc(url):
    #return urlsplit(url).netloc
    return tldextract.extract(url).domain
