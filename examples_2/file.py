class File:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        print("Opening file or reading")
        file = open(self.file_path, "r+")
        all_data = file.read()
        # Method sets the current file position in a file stream
        # Method also returns the new position
        file.seek(0)
        all_lines = file.readlines()
        file.seek(0)
        b_r = file.read(20)
        file.seek(0)
        line_read = file.readline()
        if not file.closed:
            print("Closing file...")
            file.close()
        print("All data: " + str(all_data))
        print("---------------------\n")
        print("Lines:")
        for i, line in enumerate(all_lines):
            print("#: " + str(i) + ": " + str(line))
        print("---------------------\n")
        b_l = str(len(b_r))
        print("Buffered : (" + b_l + ") -" + str(b_r))
        print("---------------------\n")
        print("Line read: " + str(line_read))
        print("---------------------\n")


filename = './file.txt'
obj = File(filename)
obj.read()
