# import json
# import time
# import requests
# from os.path import exists


# class AnnapurnaPostScrapper:
#     def __init__(self,):
#         self.headers = {
#             "User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36",
#         }
#         self.params = {
#             "title": "",
#             "page": None
#         }
#         self.url = "https://bg.annapurnapost.com/api/search"
#         self.filename = 'news.json'
    
#     def request_url(self,):
#         try:
#             response = requests.get(self.url, headers=self.headers, params=self.params)
#             status_code = response.status_code
#             response = response.json()
#             return response, status_code
#         except:
#             return False

#     def scrape_annapurnapost(self, search_term, pages_to_scrape, ):

#         self.params['title'] = search_term
        
#         target_no_of_pages = pages_to_scrape
#         page = 1
#         file_exist = exists(self.filename)
#         pages_scrapped, total_pages = 0, 0
#         articles = []

#         if not file_exist:
#             json_to_write = {
#                 "total_pages": 0,
#                 "pages_scrapped": 0,
#                 "articles": []
#             }
#             news_file =  open(self.filename, 'w+')
#             json.dump(json_to_write, news_file, 
#                 indent=4,  
#                 separators=(',',': '), ensure_ascii=False)

#         else:
#             with open(self.filename) as _file:
#                 news_file = json.load(_file)
#                 pages_scrapped = news_file['pages_scrapped']
#                 articles = news_file['articles']
#                 total_pages = news_file['total_pages']

#         while pages_scrapped < target_no_of_pages:
#             print( f'Scrapping page: {pages_scrapped+1}....')
#             self.params['page'] = pages_scrapped + 1
#             response, status_code = self.request_url()
#             if status_code == 200:
#                 total_pages = response['data']['totalPage']
#                 articles = articles + response['data']['items']
#                 articles = self.append_to_file(articles, total_pages , pages_scrapped+1)

#                 if pages_scrapped == 0:
#                     if total_pages < target_no_of_pages:
#                         print(f'Total available page is less than input pages. So scraping contents of {total_pages} pages only.')
#                         target_no_of_pages = total_pages
#             elif status_code==404 and total_pages == pages_scrapped:
#                 break
#             else:
#                 print(f'Some error occured in page {page}. Skipping..')
#                 pages_scrapped += 1
#                 continue
#             pages_scrapped += 1

#         print(f'News articles saved to {self.filename}')


#     def append_to_file(self, data, total_pages, pages_scrapped):
#         # with open(self.filename) as _file:
#         #     news_file = json.load(_file)
#         #     pages_scrapped = news_file['pages_scrapped']
#         #     articles = news_file['articles']
        
#         json_to_write = {
#             "total_pages": total_pages,
#             "pages_scrapped": pages_scrapped ,
#             "articles": data
#         }
#         with open(self.filename, 'w+', encoding='utf-8') as json_file:
#             json.dump(json_to_write, json_file, 
#                 indent=4,  
#                 separators=(',',': '), ensure_ascii=False)
#         return data
# #First argument is search term and second argument is number of target pages to scrape 
# AnnapurnaPostScrapper().scrape_annapurnapost('बर्डफ्लु', 200)



def dict_validate(input_dict, rule):
    if isinstance(input_dict, dict) :
        return all(key in rule and dict_validate(input_dict[key], rule[key]) for key in input_dict)


if isinstance(struct, dict) and isinstance(conf, dict):
        # struct is a dict of types or other dicts
        return all(k in conf and check_structure(struct[k], conf[k]) for k in struct)
    if isinstance(struct, list) and isinstance(conf, list):
        # struct is list in the form [type or dict]
        return all(check_structure(struct[0], c) for c in conf)
    elif isinstance(struct, type):
        # struct is the type of conf
        return isinstance(conf, struct)
    else:
        # struct is neither a dict, nor list, not type
        return False