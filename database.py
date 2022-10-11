class Database:
    def __init__(self):
        self.insert_database = {}
        self.delete_database = {}

    def ReadFile(self, file_name):
        f = open(file_name, 'r')
        lines = f.readlines()
        sid, operation, event = "", "", []
        self.insert_database.clear()
        self.delete_database.clear()
        for line in lines:
            l = line.strip().split(' ')
            sid = int(l[0].strip())
            operation = int(l[1].strip())
            if operation == 0:
                self.insert_database[sid] = []
                self.insert_database[sid].append([])
                for i in range(2, len(l)-1):
                    item = int(l[i].strip())
                    if item < 0:
                        if i == len(l)-2:
                            break
                        self.insert_database[sid].append([])
                    else:
                        self.insert_database[sid][-1].append(item)
        return

    def PrintDatabase(self):
        for key in self.insert_database:
            print("sid = ", key)
            print("events = ", self.insert_database[key])
        return
