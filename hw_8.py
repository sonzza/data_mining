from os import path
import os
import PyPDF2
from PyPDF2.utils import PdfReadError
from PIL import Image
import pytesseract

from pymongo import MongoClient

pdf_file_path = '/Users/sonzza/PycharmProjects/data_mining/data_for_parse/'
image_folder_path = '/Users/sonzza/PycharmProjects/data_mining/image'
pdf_result = []
pdf_non_result = []


def extract_pdf_image(pdf_path):
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

        if page_obj['/Im0'].get('/Subtype') == '/Image':
            size = (page_obj['/Im0']['/Width'], page_obj['/Im0']['/Height'])
            data = page_obj['/Im0']._data

            mode = 'RGB' if page_obj['/Im0']['/ColorSpace'] == '/DeviceRGB' else 'P'

            decoder = page_obj['/Im0']['/Filter']
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
    file_paths = []
    for itm in pdf_strict:
        name = f'{file_name}_#_{itm["page"]}.{itm["file_type"]}'
        file_path = path.join(f_path, name)

        with open(file_path, 'wb') as image:
            image.write(itm['data'])
        file_paths.append(file_path)
    return file_paths


def extract_number(file_path):
    numbers = []
    img_obj = Image.open(file_path)
    text = pytesseract.image_to_string(img_obj, 'rus')
    text_en = pytesseract.image_to_string(img_obj, 'eng')
    pattern = 'заводской (серийный) номер'
    pattern_2 = 'заводской номер (номера)'

    for idx, line in enumerate(text.split('\n')):
        if line.lower().find(pattern) + 1:
            number = text_en.split('\n')[idx].split(' ')[-1]
            numbers.append(number)
        elif line.lower().find(pattern_2) + 1:
            number = text_en.split('\n')[idx - 2].split(' ')[-1]
            numbers.append(number)
    return numbers


if __name__ == '__main__':
    client_mongo = MongoClient('mongodb://127.0.0.1:27017/')
    db = client_mongo['data_for_parse']

    for root, dirs, files in os.walk(pdf_file_path):

        for file in files:
            path_addr = root + file
            if file.endswith('.pdf'):
                try:
                    image_pdf = extract_pdf_image(path_addr)
                    try:
                        save_image = save_pdf_image(file, image_folder_path, *image_pdf)
                        extract = {}
                        for i in range(0, len(save_image)):
                            extract[str(i)] = extract_number(save_image[i])
                        info = {'file_name': file, 'path': os.path.join(root, file), 'result': extract}
                        pdf_result.append(info)
                    except:
                        info = {'file_name': file, 'address': os.path.join(root, file), 'result': "Can't find number"}
                        pdf_non_result.append(info)
                        print(file)
                except:
                    info = {'file_name': file, 'address': os.path.join(root, file), 'result': "Can't read"}
                    pdf_non_result.append(info)
                    print(file)

            elif file.endswith('.jpg'):
                try:
                    extract = {'0': extract_number(root + '/' + file)}
                    info = {'file_name': file, 'path': os.path.join(root, file), 'result': extract}
                    pdf_result.append(info)
                except:
                    info = {'file_name': file, 'address': os.path.join(root, file), 'result': "Can't find number"}
                    pdf_non_result.append(info)
                    print(file)

    # pdf_a = extract_files_pdf_path(pdf_file_path)

    # for root, dirs, files in os.walk(pdf_file_path):
    #     for file in files:
    #         o = root + file
    #         if file.endswith('.pdf'):
    #             a = extract_pdf_image(o)
    #             b = save_pdf_image(file, image_folder_path, *a)
    #             c = [extract_number(itm) for itm in b]

    db['sn'].insert_many(pdf_result)
    db['no_sn'].insert_many(pdf_non_result)
