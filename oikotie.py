from bs4 import BeautifulSoup
import requests
import time
import pandas as pd

t0 = time.time()

house_id = "15712871" #"15711635"
house_id_stop = 15732880 #15711650
house_row_data = []
final_data = ''
data = []
houses = []
data_rows = 0
total_rows_parsed = 0
i = 0
delimiter = '€'

headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'}

# Looping through the html pages and collecting the data.
while int(house_id) < house_id_stop:
    URL = "https://asunnot.oikotie.fi/myytavat-asunnot/helsinki/" + house_id

    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')

    house_sale_notice = soup.find_all('span', {'class': 'listing-breadcrumbs__item'})

    if house_sale_notice:
        if house_sale_notice[0].get_text() == 'Myytävät asunnot':
            info_table_row = soup.find_all('div', {'class': 'info-table__row'})
            if info_table_row:
                while i < len(soup.find_all('dd', {'class': 'info-table__value'})):

                    if i == 0:
                        house_row_data.append(house_id)

                    #print(info_table_row[i].get_text())
                    #print(info_table_row[i].findChildren("dt")[0].get_text()) #tiedon title
                    # print(info_table_row[i].findChildren("dd")[0].get_text()) #itse tieto

                    info_table_title = info_table_row[i].findChildren("dt")

                    if info_table_title:
                        if info_table_title[0].get_text() == 'Sijainti':
                            house_row_data.append(str(info_table_row[i].findChildren("dd")[0].findChildren("a")[1].get_text())) #postikoodi
                            house_row_data.append(str(info_table_row[i].findChildren("dd")[0].findChildren("a")[2].get_text())) #kaupunki

                        if info_table_row[i].findChildren("dt")[0].get_text() == 'Kaupunginosa':
                            house_row_data.append(str(info_table_row[i].findChildren("dd")[0].findChildren("a")[0].get_text())) #kaupunginosa

                        if info_table_row[i].findChildren("dt")[0].get_text() == 'Asuinpinta-ala':
                            house_row_data.append(str(info_table_row[i].findChildren("dd")[0].get_text()).replace(' m²', '')) #asuinpinta-ala

                        if info_table_row[i].findChildren("dt")[0].get_text() == 'Huoneita':
                            house_row_data.append(str(info_table_row[i].findChildren("dd")[0].get_text())) #huoneita

                        if info_table_row[i].findChildren("dt")[0].get_text() == 'Kunto':
                            house_row_data.append(str(info_table_row[i].findChildren("dd")[0].get_text())) #kunto

                        if info_table_row[i].findChildren("dt")[0].get_text() == 'Myyntihinta':
                            house_row_data.append(str(info_table_row[i].findChildren("dd")[0].get_text()).replace("€", '')) #Myyntihinta

                    i += 1
                final_data = "€".join(house_row_data)
                house_row_data.clear()
                print(final_data)
                data.append(final_data.split(delimiter))
                i = 0
                data_rows += 1

    house_id = str(int(house_id) + 1)
    total_rows_parsed += 1

print(data)
t1 = time.time()
total = t1-t0
print("Parser in total", total_rows_parsed, "rows.")
print("Time lapsed in total", total)
print("Time for one URL", total/total_rows_parsed)