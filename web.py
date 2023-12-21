import requests
from bs4 import BeautifulSoup
import openpyxl
from datetime import datetime



# headers 
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
def scrape_artist_data(url):
   
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        artist_names=[]
        artist_url=[]
        images=[]
        ages=[]

        for name in soup.select('.ipc-metadata-list-item--link .ipc-metadata-list-item__content-container .ipc-inline-list__item .ipc-metadata-list-item__list-content-item'):
            #Since each actor names are repeated twice 
            if name.text in artist_names:
                break
            else:
                artist_names.append(name.text)
                artist_url.append(name['href'])
        
        
        for artisturl,artistname in zip(artist_url,artist_names):
            response = requests.get(f'https://m.imdb.com{artisturl}', headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')


            for image in soup.select('.ipc-image'):
                if image['alt']!=artistname:
                    break
                images.append(image['src'])
                break


            for age in soup.select('.sc-dec7a8b-2'):
                if age.text=="Born":
                    continue
                
                birthdate = datetime.strptime(age.text, "%B %d, %Y")
                current_date = datetime.now()
                age = current_date.year - birthdate.year - ((current_date.month, current_date.day) < (birthdate.month, birthdate.day))
                ages.append(age)
                break
        
        return artist_names, ages, images
    else:
        print('Failed to retrieve the web page. Status code:', response.status_code)
        return None


def save_to_excel(artist_names, ages, images,sheet):

    for artist, age, image in zip(artist_names, ages, images):
        sheet.append([artist, age, image])


# main starts 
main_url='https://m.imdb.com/chart/top/'
response = requests.get(main_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.append(['Artist Name', 'Age', 'Image'])
i=1
for movie_url in soup.select('.ipc-title-link-wrapper'):
    if i==10:
        break
    i=i+1
    movie_url_title_checker=movie_url['href'].split('/')
    if movie_url_title_checker[1]!='title':
        break

    artist_data = scrape_artist_data(f'https://m.imdb.com{movie_url["href"]}')
   
    if artist_data:
        save_to_excel(*artist_data,sheet)

workbook.save('scraped_data.xlsx')
print(f'Data saved ')

