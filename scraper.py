from seleniumbase import SB
from bs4 import BeautifulSoup
import urllib.parse
import time

def run_scraper(df):
    with SB(uc=True, test=True, headless=False) as sb:  
        url = f"https://www.BING.com"
        sb.activate_cdp_mode(url)
        start = time.time()
        for index, row in df.iterrows():
            try:
                query = f"{row.get('Name','')} {row.get('Designation','')} {row.get('Company Name','')} {row.get('City','')} linkedin"
                search_query = urllib.parse.quote(query)
                search = f"https://www.google.com/search?q={search_query}"
                sb.open(search)
                sb.sleep(8)
                soup = BeautifulSoup(sb.get_page_source(), 'html.parser')
                linkedin_url = ""
                for a_tag in soup.find_all('a'):
                    href = a_tag.get('href')
                    if href and 'linkedin.com/in/' in href:
                        linkedin_url = href
                        lnk = a_tag.find_parent('div').find_parent('div').find_parent('div').find_parent('div')
                        if lnk and lnk.find('span',{'class' : 'VuuXrf'}) != None:
                            lstn = lnk.find('span',{'class' : 'VuuXrf'}).text.split('·')
                            df.at[index, 'Linkedin_name'] = lstn[-1].replace('\xa0', '')  
                        if lnk and lnk.find_parent('div').find_parent('div').find('div',{'class': 'YrbPuc'}) != None:
                            r = lnk.find_parent('div').find_parent('div').find('div',{'class': 'YrbPuc'}).find_all('span')
                            lst = [l.text for l in r if l.text != ' · ']
                            if len(lst) < 2: 
                                df.at[index, 'location'] = lst[0]
                            elif len(lst) < 3:
                                df.at[index, 'location'] = lst[0]
                                df.at[index, 'company'] = lst[1]                                
                            else:
                                df.at[index, 'designation'] = lst[1]
                                df.at[index, 'company'] = lst[2]
                                df.at[index, 'location'] = lst[0]
                        break
                df.at[index, 'linkedin_url'] = linkedin_url
            except Exception as e:
                print("Error:", e)
        print(f"Time elapsed: {time.time()-start} seconds")
    return df
