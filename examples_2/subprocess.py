import chardet

import subprocess


class SP:
    @staticmethod
    def execute(command, args=""):
        try:
            p = subprocess.Popen(command + " " + str(args), shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            print("ID of spawned process is: " + str(p.pid) + "\n")
            out, err = p.communicate()
            result = chardet.detect(out)
            print(result)
            out = str(out).encode('ascii')
            out = out.decode('utf-8')
            splitted = str(out).split("\\n")
            for o in splitted:
                print(o)
        except Exception as ex:
            print("Exception caught: " + str(ex))


SP.execute("ls")
