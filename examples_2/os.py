import os


class OsDirectories:
    def __init__(self):
        # Get current working directory
        self.path_parent_0 = os.getcwd()

        # Get the canonical path
        # of the specified path
        # by eliminating any symbolic links
        # encountered in the path
        self.file_path = os.path.realpath(__file__)

        # Get the directory name
        # from the specified path
        self.pr = os.path.dirname(self.file_path)

    def traverse(self, path, tr_all=False):
        if not tr_all:
            # Get the list of all files and directories in the specified directory
            files = os.listdir(path)
            for i in files:
                # Check whether the specified path is an existing directory or not
                if os.path.isdir(os.path.join(path, i)):
                    directory = str(os.path.join(path, i))
                    print("Dir: " + directory)
                    self.traverse(os.path.join(path, i))
                else:
                    print(os.path.join(path, i))
        else:
            # os.walk() - Generates the file names in a directory tree by walking the tree either top-down or bottom-up
            for root, dirs, files in os.walk(path):
                for f in files:
                    print(f)


path_name = './'
obj = OsDirectories()
obj.traverse(path_name)
