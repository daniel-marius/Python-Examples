import json


class JSONParse:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path

    def print_file(self):
        with open(self.json_file_path, "r") as json_file:
            json_data = json.loads(json_file.read())
        if json_data:
            print("Type of loaded file is :" + str(type(json_data)))
            employee_root = json_data.get("employees", None)
            if employee_root:
                print("Department : " + employee_root["department"])
                print("Location : " + employee_root["location"])
                print("Employees : ")
                for emp in employee_root["data"]:
                    print("\n-----------------------")
                    for k, v in emp.items():
                        print("\t" + str(k) + " : " + str(v))

    def process(self):
        with open(self.json_file_path, "r") as json_file:
            json_data = json.loads(json_file.read())
        if json_data:
            print("\nProcessing started...")
            for index, emp in enumerate(json_data["employees"]["data"]):
                if emp["salary"] >= 30000:
                    json_data["employees"]["data"][index]["slab"] = "A"
                else:
                    json_data["employees"]["data"][index]["slab"] = "B"
            print("Processing ended... \nSaving results :")
            with open(self.json_file_path, "w") as json_file:
                json.dump(json_data, json_file, indent=4, sort_keys=True)
            print("Results saved \nNow printing: ")
            self.print_file()


file_path = './employees.json'
obj = JSONParse(file_path)
obj.process()
