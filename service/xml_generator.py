import xml.etree.ElementTree as ET
from xml.dom import minidom


class XMLgenerator:

    def __init__(self):
        pass

    @classmethod
    def generate_from_dict(cls, file_path, params_data, types_dict, fop_path):
        def create_controlled_parameter(parent_node, name, value, is_instance="false"):
            """Вспомогательная функция для создания блока параметра"""
            param = ET.SubElement(parent_node, "ControlledParameter")
            ET.SubElement(param, "Name").text = name
            ET.SubElement(param, "Group").text = "Text"
            if value is not None:
                ET.SubElement(param, "Value").text = str(value)
            ET.SubElement(param, "IsInstance").text = is_instance
    
        # 1. Создаем корневой элемент с атрибутами пространств имен
        root = ET.Element("ParameterConfig", {
            "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
        })

        
        ET.SubElement(root, "SharedParameterFilePath").text = fop_path

        # 3. Создаем контейнер для параметров
        parameters_node = ET.SubElement(root, "Parameters")

        # 4. Цикл создания ControlledParameter
        for name, value in params_data:
            param = ET.SubElement(parameters_node, "ControlledParameter")
            
            ET.SubElement(param, "Name").text = name
            ET.SubElement(param, "Group").text = "Text"
            
            if value is not None:
                ET.SubElement(param, "Value").text = value
                
            ET.SubElement(param, "IsInstance").text = "false"

        # Узел <Types>
        types_node = ET.SubElement(root, "Types")
        for key, data in types_dict.items():
        # Создаем узел типа (например, <type1>)
            type_entry = ET.SubElement(types_node, "TypeItem")
            
            # Добавляем свойство Name для типа (например, <Name>foo</Name>)
            ET.SubElement(type_entry, "Name").text = data["name"]
            
            # Создаем контейнер <Parameters> внутри типа
            params_container = ET.SubElement(type_entry, "Parameters")
            
            # Проходим по вложенному словарю parameters
            for p_name, p_value in data["parameters"].items():
                param = ET.SubElement(params_container, "ControlledParameter")
                ET.SubElement(param, "Name").text = p_name
                ET.SubElement(param, "Group").text = "Text"
                
                if p_value is not None:
                    ET.SubElement(param, "Value").text = str(p_value)
                
            ET.SubElement(param, "IsInstance").text = "false"

        # 5. Форматирование (Pretty Print)
        xml_str = ET.tostring(root, encoding='utf-8')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ", encoding="utf-8")

        # 6. Запись в файл
        with open(file_path, "wb") as f:
            f.write(pretty_xml)


if __name__ == "__main__":
    # 2. Добавляем путь к ФОП
    fop_path = r"C:\Users\eliseev_i\Yandex.Disk\_revit_library\project_templates\ФОП2021.txt"
    params_data = [
        ("ADSK_Наименование", None),
        ("ADSK_Количество", "1"),
        ("ADSK_Марка", None),
        ("ADSK_Код изделия", None),
        ("ADSK_Завод-изготовитель", None),
        ("ADSK_Техническая характеристика", None),
        ("ADSK_Единица измерения", "шт."),
        ("ADSK_Масса", None),
    ]
    types_dict = {
        "type1": {
            "name": "foo",
            "parameters": {
                "ADSK_Наименование": None,
                "ADSK_Количество": "1",
                "ADSK_Марка": None,
                "ADSK_Код изделия": None,
                "ADSK_Завод-изготовитель": None,
                "ADSK_Техническая характеристика": None,
                "ADSK_Единица измерения": "шт.",
                "ADSK_Масса": None,
            }
        },
        "type2": {
            "name": "foo",
            "parameters": {
                "ADSK_Наименование": None,
                "ADSK_Количество": "1",
                "ADSK_Марка": None,
                "ADSK_Код изделия": None,
                "ADSK_Завод-изготовитель": None,
                "ADSK_Техническая характеристика": None,
                "ADSK_Единица измерения": "шт.",
                "ADSK_Масса": None,
            }
        },
    }

    result_xml = r'C:\Users\eliseev_i\AppData\Roaming\Autodesk\Revit\Addins\params_to_add.xml'

    XMLgenerator.generate_from_dict(
        file_path=result_xml,
        params_data=params_data,
        types_dict=types_dict,
        fop_path=fop_path)
