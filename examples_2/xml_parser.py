import xml.etree.ElementTree as ET


# XML Data Manipulation
class XMLParser:
    def __init__(self, xml):
        self.xml = xml

    def parse(self, parse_type="doc"):
        if parse_type == "doc":
            root = ET.parse(self.xml).getroot()
        else:
            root = ET.fromstring(self.xml)
        tag = root.tag
        print("Root tag is: " + str(tag))
        attributes = root.attrib
        print("Root attributes are: ")
        for k, v in attributes.items():
            print("\t" + str(k) + " : " + str(v))
        print("\nPrinting node details without knowing subtag :")
        for employee in root:
            print("\n--------------------")
            for element in employee:
                ele_name = element.tag
                ele_value = employee.find(element.tag).text
                print("\t\t" + ele_name, ' : ', ele_value)

        print("\n\nPrinting node details specifying subtag :")
        for employee in root.findall("employee"):
            print("\n--------------------")
            print("\t\tName :" + str(employee.find("name").text))
            print("\t\tSalary :" + str(employee.find("salary").text))
            print("\t\tAge :" + str(employee.find("age").text))
            print("\t\tManager Id :" + str(employee.find("manager_id").text))
            print("\t\tDOJ :" + str(employee.find("doj").text))


xml_file = './employees.xml'
obj = XMLParser(xml_file)
obj.parse()
