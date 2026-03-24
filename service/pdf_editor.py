# -*- coding: utf-8 -*-
import json
import os
import glob
import logging

from PyPDF2 import PdfReader, PdfWriter
from pprint import pprint


class PDFeditor:
    source_dir: str
    floor_id: str
    section_id: str
    logger: logging.Logger

    def __init__(self, source_dir):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.source_dir = source_dir

    def edit_pdf_and_json(self, pdf_path, json_path):
        json_data = self.read_json(path=json_path)
        proj_data = json_data['project_data']
        # pprint(proj_data)

        width_crop = proj_data['full_image_width_mm'] / \
            proj_data['format_width_mm']
        height_crop = proj_data['full_image_height_mm'] / \
            proj_data['format_height_mm']

        file_name = os.path.split(pdf_path)[1].replace('.pdf', '')
        level_name = proj_data['floor_id']
        output_file_name = file_name + '_этаж-' + str(level_name)

        pdf_data = self.crop_pdf(
            width_ratio=width_crop,
            height_ratio=height_crop,
            input_file=pdf_path,
            output_file=output_file_name + '.pdf',
        )

        tiles_updated = self.update_tiles_json(
            tiles_data=json_data,
            pdf_data=pdf_data,
            _file_path=json_path,
            output_file=output_file_name + '.json'
        )

        os.remove(pdf_path)
        os.remove(json_path)

    def update_tiles_json(self, _file_path, output_file, tiles_data: dict, pdf_data: dict) -> bool:

        def transliterate(input_str):
            char_map = {
                'с': 'c',
                'А': 'A',
                'Б': 'B',
                'В': 'V',
                'Г': 'G',
                'Д': 'D',
                'Е': 'E',
                'Ё': 'Y',
                'Ж': 'J',
                'З': 'Z',
                'И': 'I',
                'К': 'K',
                'Л': 'L',
                'М': 'M',
                'Н': 'N',
                'О': 'O',
                'П': 'P',
                'Р': 'R',
                'С': 'S',
                'Т': 'T',
                'У': 'U',
                'Ф': 'F',
                'Х': 'H',
                'Ц': 'C',
                'Ш': 'sh',
                'Щ': 's_h',
                'Э': 'ye',
                'Ю': 'yu',
                'Я': 'ya',
            }
            result = str()

            reversed_char_map = dict()
            for origin, replacement in char_map.items():
                reversed_char_map[replacement] = origin

            for char in input_str:
                if char in reversed_char_map:
                    result += reversed_char_map[char]
                else:
                    result += char

            return result

        def update_tile(_tile_data: dict) -> dict:
            new_dict = {
                'pdf_y': tiles_start_y - tile_length_pix * (int(_tile_data['row']) - 1),
                'pdf_x': tiles_start_x + tile_length_pix * (int(_tile_data['column']) - 1),
                'column': _tile_data['column'],
                'row': _tile_data['row'],
                'project_y': _tile_data['project_y'],
                'project_x': _tile_data['project_x'],
                'axes': _tile_data['axes']
            }
            return new_dict

        tiles_list = tiles_data['tiles']
        project_data = tiles_data['project_data']

        # self.floor_id = project_data['floor_id']
        self.section_id = project_data['section_id']

        result_data = dict()
        result_data['project_data'] = tiles_data['project_data']
        result_data['pdf_data'] = pdf_data

        pix_to_mm_ratio = pdf_data['cropped_width'] / \
            project_data['full_image_width_mm']
        result_data['pdf_data']['pix_to_mm_ratio'] = pix_to_mm_ratio

        tile_length_pix = int(
            project_data['tile_side_mm'] * pix_to_mm_ratio / 100)
        result_data['pdf_data']['tile_length_pix'] = tile_length_pix

        tiles_start_x = int(
            (pdf_data['cropped_width'] - project_data['tiles_columns'] * tile_length_pix) / 2)
        result_data['pdf_data']['tiles_start_x'] = tiles_start_x

        tiles_start_y = int(
            (pdf_data['cropped_height'] - project_data['tiles_rows'] * tile_length_pix) / 2 + project_data[
                'tiles_rows'] * tile_length_pix)
        result_data['pdf_data']['tiles_start_y'] = tiles_start_y

        # pprint(result_data['pdf_data'])

        tiles_updated_data = dict()
        for tile_data in tiles_list:
            # pprint(tile_data)
            tiles_updated_data[tile_data['number']] = update_tile(tile_data)
        result_data['tiles'] = tiles_updated_data

        dir_path = os.path.split(_file_path)[0]
        new_file_path = os.path.join(dir_path, output_file)

        # pprint(result_data)
        self.logger.info(f'[{__name__}]: writing updated json')
        with open(new_file_path, 'w', encoding='utf8') as f:
            json.dump(obj=result_data, fp=f, indent=2, ensure_ascii=False)

        return True

    def get_files_list(self) -> list:

        def lookup_latest_files(path, file_type) -> list:
            lookup_path = os.path.join(path, '*.' + file_type)
            list_of_files = glob.glob(lookup_path)
            # latest_file = max(list_of_files, key=os.path.getctime)
            # print(f'[{__name__}]: latest {file_type} file: {latest_file}')
            return list_of_files

        json_files = lookup_latest_files(self.source_dir, 'json')
        pdf_files = lookup_latest_files(self.source_dir, 'pdf')

        files_list = list(zip(pdf_files, json_files))
        self.logger.info(
            f'[{__name__}]: found {len(files_list)} pdf files with corresponding json')
        return files_list

    def read_json(self, path) -> dict:
        print(path)
        with open(path, encoding='utf-8') as f:
            _dict = json.load(f)

        return _dict

    def crop_pdf(self, input_file: str, output_file: str, width_ratio: float, height_ratio: float) -> dict:

        _pdf_data = dict()

        with open(input_file, "rb") as in_f:
            reader = PdfReader(in_f)
            page = reader.pages[0]

            original_width = page.mediabox.width
            original_height = page.mediabox.height

            if page.rotation == 0:
                _pdf_data['original_width'] = original_width
                _pdf_data['original_height'] = original_height
                self.logger.info(
                    f'[{__name__}]: original width/height: {original_width} / {original_height}')
                cropped_width = int(original_width * width_ratio)
                cropped_height = int(original_height * height_ratio)

                page.cropbox.lower_left = (0, 0)
                page.cropbox.upper_right = (cropped_width, cropped_height)

            if page.rotation == 90:
                _pdf_data['original_width'] = original_height
                _pdf_data['original_height'] = original_width
                self.logger.info(
                    f'[{__name__}]: original width/height: {original_height} / {original_width}')

                cropped_width = int(original_height * width_ratio)
                cropped_height = int(original_width * height_ratio)

                lower_left_x = original_width - cropped_height
                page.cropbox.lower_left = (
                    (original_width - cropped_height), 0)
                page.cropbox.upper_right = (original_height, cropped_width)

            _pdf_data['cropped_width'] = cropped_width
            _pdf_data['cropped_height'] = cropped_height
            self.logger.info(
                f'[{__name__}]: new width/height: {cropped_width} / {cropped_height}')

            writer = PdfWriter()
            writer.add_page(page)

        dir_path = os.path.split(input_file)[0]
        new_file_path = os.path.join(dir_path, output_file)

        with open(new_file_path, "wb") as out_f:
            writer.write(out_f)

        return _pdf_data


if __name__ == '__main__':
    editor = PDFeditor()
    for pdf_file, json_file in editor.get_files_list():
        editor.edit_pdf_and_json(pdf_path=pdf_file, json_path=json_file)
