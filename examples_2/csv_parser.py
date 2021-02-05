import csv


class CSVParser:
    def __init__(self, _csv):
        self.csv = _csv
        self.employees = []

    def parse(self):
        print("\n(M1): Reading with reader")
        with open(self.csv) as csv_file:
            read_csv = csv.reader(csv_file, delimiter=',')
            header = next(read_csv)
            print("Header is: " + str(header))
            print()
            new_header = header[0] + "\t" + header[1] + "\t" + header[2] + "\t" + header[3] + "\t" + header[4]
            print(new_header)
            for index, row in enumerate(read_csv):
                if len(row):
                    values = row[0] + "\t" + row[1] + "\t" + row[2] + "\t" + row[3] + "\t" + row[4]
                    print(values)
                    employee = {
                        header[0]: row[0],
                        header[1]: row[1],
                        header[2]: row[2],
                        header[3]: row[3],
                        header[4]: row[4]
                    }
                    self.employees.append(employee)
        print("\n(M2) : Reading with DictReader")
        with open(self.csv) as csv_file:
            reader = csv.DictReader(csv_file)
            header = reader.fieldnames
            new_header = header[0] + "\t" + header[1] + "\t" + header[2] + "\t" + header[3] + "\t" + header[4]
            print("\n" + new_header)
            for ind, row in enumerate(reader):
                values = row["Name"] + "\t" + row["Age"] + "\t" + row["Salary"] + "\t" + row["M_id"] + "\t" + \
                         row["Slab"]
                print(values)

    def process(self):
        for emp in self.employees:
            if int(emp["Salary"]) >= 30000:
                emp["Slab"] = "A"
            else:
                emp["Slab"] = "B"
        header = self.employees[0].keys()
        print(self.employees)
        print("\n(M1) : Writing with DictWriter ")
        with open(self.csv, "w") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=header)
            writer.writeheader()
            writer.writerows(self.employees)
        print("Data written ! \n")
        self.parse()


csv_file_path = './employees.csv'
obj = CSVParser(csv_file_path)
obj.parse()
obj.process()
