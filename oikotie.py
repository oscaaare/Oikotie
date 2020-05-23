from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from datetime import datetime

t0 = time.time()
script_started = datetime.now()

fname = 'Oikotie_houses_for_sale'+datetime.now().strftime("%d_%m_%Y")+'.xlsx'
fname2 = 'Oiktoie_empty_rows'+datetime.now().strftime("%d_%m_%Y")+'.xlsx'
house_id = "5538385"# 5252117 pitäisi olla ensimmäinen
house_id_stop = 5538386 #15716055 pitäisi olla viimeinen
delimiter = '€'
headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'}


# Looping through the html pages and collecting the data.
def collect_data(headers_def, house_id_def, house_id_stop_def, delimiter_def):
    house_row_data = []
    empty_house_ids_def = []
    not_sale_house_ids_def = []
    final_data = ''
    data_def = []
    help_title_list = []
    data_rows = 0
    total_rows_parsed_def = 0
    i = 0
    data_rows_parsed_def = 0
    tasaluku = int(house_id_def)

    while int(house_id_def) < house_id_stop_def:
        url = "https://asunnot.oikotie.fi/myytavat-asunnot/helsinki/" + house_id_def

        page = requests.get(url, headers=headers_def)
        soup = BeautifulSoup(page.content, 'lxml')
        message = ''

        house_sale_notice = soup.find_all('span', {'class': 'listing-breadcrumbs__item'})

        if house_sale_notice:
            if house_sale_notice[0].get_text() == 'Myytävät asunnot':
                info_table_row = soup.find_all('div', {'class': 'info-table__row'})
                if info_table_row:
                    while i < len(soup.find_all('dd', {'class': 'info-table__value'})):
                        if i == 0:
                            house_row_data.append(house_id_def)
                            data_rows_parsed_def += 1

                        info_table_title = info_table_row[i].findChildren("dt")
                        info_table_value = info_table_row[i].findChildren("dd")

                        if info_table_title:

                            info_table_title_text = info_table_title[0].get_text()

                            if info_table_title_text == 'Sijainti':
                                try:
                                    house_row_data.append(
                                        str(info_table_value[0].findChildren("a")[1].get_text())[:5]) #postikoodi
                                    help_title_list.append(0)
                                except:
                                    pass


                            if info_table_title_text == 'Sijainti':
                                try:
                                    house_row_data.append(
                                        str(info_table_value[0].findChildren("a")[2].get_text()))  # kaupunki
                                    help_title_list.append(1)
                                except:
                                    pass

                            if info_table_title_text == 'Kaupunginosa':
                                try:
                                    house_row_data.append(str(info_table_value[0].get_text())) #Kaupunginosa
                                    help_title_list.append(2)
                                except:
                                    pass

                            if info_table_title_text == 'Asuinpinta-ala':
                                try:
                                    house_row_data.append(
                                        str(info_table_value[0].get_text()).replace(
                                            ' m²', '').replace(
                                            ',', '.')) #asuinpinta-ala
                                    help_title_list.append(3)
                                except:
                                    pass

                            if info_table_title_text == 'Huoneita':
                                try:
                                    house_row_data.append(str(info_table_value[0].get_text())) #huoneita
                                    help_title_list.append(4)
                                except:
                                    pass

                            if info_table_title_text == 'Kunto':
                                try:
                                    house_row_data.append(str(info_table_value[0].get_text())) #kunto
                                    help_title_list.append(5)
                                except:
                                    pass

                            if info_table_title_text == 'Myyntihinta':
                                try:
                                    house_row_data.append(
                                        str(info_table_value[0].get_text()).replace(
                                            "€", '').replace(
                                            '\xa0', '').replace(
                                            ',', '.')) #Myyntihinta
                                    help_title_list.append(6)
                                except:
                                    pass

                        i += 1

                    num = 0
                    help_num = 0
                    while num < len(help_title_list):
                        if help_title_list[num] == help_num:
                            help_num += 1
                        else:
                            help_num += 1
                            house_row_data.insert(help_num, '')
                            help_num += 1
                        num += 1

                    try:
                        house_row_data.append(str(round(float(house_row_data[7]) / float(house_row_data[4]), 2))) #neliöhinta
                    except:
                        house_row_data.append(str('')) #neliöhinta, jos neliöt on nolla

                    final_data = "€".join(house_row_data)
                    house_row_data.clear()
                    help_title_list.clear()
                    print(final_data)
                    data_def.append(final_data.split(delimiter_def))
                    i = 0
                    data_rows += 1
            else:
                not_sale_house_ids_def.append(house_id_def)
                message = " - URL contains data, but it isn't a sale notice"
        else:
            empty_house_ids_def.append(house_id_def)
            message = ' - Empty URL'

        if message:
            print(house_id_def + message)

        house_id_def = str(int(house_id_def) + 1)
        total_rows_parsed_def += 1

    return data_def, total_rows_parsed_def, data_rows_parsed_def, empty_house_ids_def, not_sale_house_ids_def


data, total_rows_parsed, data_rows_parsed, empty_house_ids, not_sale_house_ids = collect_data(headers, house_id, house_id_stop, delimiter)

#Creating the DataFrame.
df = pd.DataFrame(data, columns=['house_id', 'postal_code', 'city', 'city_part', 'square_meters', 'rooms', 'condition', 'sale_price', 'price_per_square_meter'])
df2 = pd.DataFrame(empty_house_ids, columns=['empty_house_ids'])

# Creating a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(fname, engine='xlsxwriter', options={'strings_to_numbers': True})
writer2 = pd.ExcelWriter(fname2, engine='xlsxwriter', options={'strings_to_numbers': True})

# Converting the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Oikotie', index=False)
df2.to_excel(writer2, sheet_name='Empty_rows', index=False)

#Creating cell formats using the xlsxwriter workbook and worksheet objects.
workbook = writer.book
workbook = writer2.book
worksheet = writer.sheets['Oikotie']
worksheet2 = writer2.sheets['Empty_rows']
format1 = workbook.add_format({'num_format': '#,##0.00'})
format2 = workbook.add_format({'num_format': '00000'})

#Applying formats to selected columns
worksheet.set_column('A:A', 10, None)
worksheet.set_column('B:B', 10, format2)
worksheet.set_column('C:C', 10, None)
worksheet.set_column('D:D', 10, None)
worksheet.set_column('E:E', 10, format1)
worksheet.set_column('F:F', 10, None)
worksheet.set_column('G:G', 10, None)
worksheet.set_column('H:H', 10, format1)
worksheet.set_column('I:I', 10, format1)

# Closing the Pandas Excel writer to output the Excel file.
writer.save()
writer2.save()

print(data)
script_ended = datetime.now()
t1 = time.time()
total_time = t1-t0
print("Script started ", script_started)
print("Script ended ", script_ended)
print("Empty URLS", empty_house_ids)
print("Not for sale URLS", not_sale_house_ids)
print("Parser in total", total_rows_parsed, "URLs.")
print("Parser in total", data_rows_parsed, "URLs with data.")
print("Time lapsed in total", total_time)
print("Time for one URL", total_time/total_rows_parsed)
