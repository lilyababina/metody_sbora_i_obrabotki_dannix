import shutil
from os import path
import os
import PyPDF2
from PyPDF2.utils import PdfReadError
from PIL import Image
import pytesseract
import time
import img2pdf
from pymongo import MongoClient


def copy_with_doubles(path1, path2, name, name2):
    if name2 not in os.listdir(path2):
        shutil.copyfile(f'{path1}/{name}',
                        f'{path2}/{name2}')
    else:
        name2 = 'copy' + name2
        copy_with_doubles(path1, path2, name, name2)

def replace_files(path_data, path_pdf_data, path_jpg_data, path_other_files):
    tree = os.walk(path_data)
    folder = []
    for i in tree:
        folder.append(i)

#for i in range(len(folder)): #смотрим структуру каталогов
#    print(folder[i])

    for i in range(len(folder)):
        for j in range(len(folder[i][2])):
            if not folder[i][2][j].endswith('.DS_Store') and not folder[i][2][j].endswith('Thumbs.db'): #системные файлы не копируем
                if folder[i][2][j].endswith('.pdf'):
                    copy_with_doubles(f'{folder[i][0]}', f'{path_pdf_data}', f'{folder[i][2][j]}', f'{folder[i][2][j]}')

                elif folder[i][2][j].endswith('.jpg'):
                    copy_with_doubles(f'{folder[i][0]}', f'{path_jpg_data}', f'{folder[i][2][j]}', f'{folder[i][2][j]}')

                else:
                    copy_with_doubles(f'{folder[i][0]}', f'{path_other_files}', f'{folder[i][2][j]}', f'{folder[i][2][j]}')

path_data = '/Users/lilyarunich/PycharmProjects/untitled1/data_for_parse/data' #изначальные даннные
path_pdf_data = '/Users/lilyarunich/PycharmProjects/untitled1/data_for_parse/pdf_data' #отсортированные pdf
path_jpg_data = '/Users/lilyarunich/PycharmProjects/untitled1/data_for_parse/jpg_data' #отсортированные jpg
path_other_files = '/Users/lilyarunich/PycharmProjects/untitled1/data_for_parse/other_files' # другие файлы
image_folder_path = '/Users/lilyarunich/PycharmProjects/untitled1/data_for_parse/image'
path_err = '/Users/lilyarunich/PycharmProjects/untitled1/data_for_parse/pdf_err'




def extract_pdf_image(pdf_path): #на вход путь к файлу с названием
    try:
        pdf_file = PyPDF2.PdfFileReader(open(pdf_path, 'rb'), strict=False)
    except PdfReadError as e:
        print(e)
        return None
    except FileNotFoundError as e:
        print(e)
        return None
    result = []
    for page_num in range(0, pdf_file.getNumPages()):
        page = pdf_file.getPage(page_num)
        page_obj = page['/Resources']['/XObject'].getObject()

        key_img = list(page_obj.keys())[0]


        if page_obj[key_img].get('/Subtype') == '/Image':
            size = (page_obj[key_img]['/Width'], page_obj[key_img]['/Height'])
            data = page_obj[key_img]._data

            mode = 'RGB' if page_obj[key_img]['/ColorSpace'] == '/DeviceRGB' else 'P'

            decoder = page_obj[key_img]['/Filter']
            if decoder == '/DCTDecode':
                file_type = 'jpg'
            elif decoder == '/FlateDecode':
                file_type = 'png'
            elif decoder == '/JPXDecode':
                file_type = 'jp2'
            else:
                file_type = 'bmp'

            result_sctrict = {
                'page': page_num,
                'size': size,
                'data': data,
                'mode': mode,
                'file_type': file_type,
            }
            result.append(result_sctrict)
    return result


def save_pdf_image(file_name, f_path, *pdf_strict):

    for itm in pdf_strict:
        name = f'{file_name}_#_{itm["page"]}.{itm["file_type"]}'
        file_path = path.join(f_path, name)

        with open(file_path, 'wb') as image:
            image.write(itm['data'])

def extract_number(file_path):
    numbers = []
    img_obj = Image.open(file_path)
    text = pytesseract.image_to_string(img_obj, 'rus')
    pattern = 'заводской (серийный) номер'

    for idx, line in enumerate(text.split('\n')):
        if line.lower().find(pattern) + 1:
            text_en = pytesseract.image_to_string(img_obj, 'eng')
            number = text_en.split('\n')[idx].split(' ')[-1]
            if number != '':
                db['numbers_from_img'].insert_one({'number': number, 'file_path': file_path})
            elif len(number) == 1:
                db['no_numbers_data_from_img'].insert_one({'file_path': file_path})
                #shutil.copyfile(file_path, f'{path_err}/{itm}')

            else:
                db['no_numbers_data_from_img'].insert_one({'file_path': file_path})
                #shutil.copyfile(file_path, f'{path_err}/{itm}')
            numbers.append((number, file_path))
    return numbers


if __name__ == '__main__':
    replace_files(path_data, path_pdf_data, path_jpg_data, path_other_files)
    #print(os.listdir(path_pdf_data))
    client = MongoClient('mongodb://localhost:27017/')
    db = client['db_blog']

    for itm in os.listdir(path_pdf_data):
        if itm != '.DS_Store':
            a = extract_pdf_image(f'{path_pdf_data}/{itm}')
            if a == None:
                print(f'файл с ошибкой - не получилось открыть: {itm}')
            else:
                b = save_pdf_image(itm, image_folder_path, *a)

    for itm in os.listdir(image_folder_path):
        if itm != '.DS_Store':
            c = extract_number(f'{image_folder_path}/{itm}')

    for itm in os.listdir(path_jpg_data):
        if itm != '.DS_Store':
            d = extract_number(f'{path_jpg_data}/{itm}')



    print('Среди данных были файлы не pdf и jpg - они на ходятся в каталоге other_files')
    print('Номера и файлы, из которых были извлечены номера находятся в коллекции numbers_from_img ')
    print('Список файлов, из которых номера не были извлечены находятся в коллекции no_numbers_data_from_img')



#todo проверить перенос файлов где не распознали серийный номер
#todo записывать в базу имена а не пути файлов где не нашли серийный номер
#todo дописать поиск по ключевому слову "Заводской номер (номера)"

#Извлечь серийные номера из файлов ( приложены в материалах урока)
#Ваша задача разобрать все фалы, распознать на них серийный номер
# и создать коллекцию в MongoDB с четким указанием из какого файла
# был взят тот или иной серийный номер.
#Дополнительно необходимо создать коллекцию и отдельную папку для
# хранения файлов в которых вы не смогли распознать серийный номер,
# если в файле встречается несколько изображений необходимо явно у
# казать что в файле таком-то страница такая серийный номер не найден.