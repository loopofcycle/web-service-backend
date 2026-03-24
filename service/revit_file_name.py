class RevitFileName:
    title: str
    project: str
    stage: str
    subpart: str
    section: str
    eir: str
    rvt: str
    incorrect: bool = False
    lib_file: bool = False

    def __init__(self, name: str):

        self.title = (str(name).
                      removesuffix('.rvt').
                      removesuffix('_отсоединено').
                      removesuffix(' (2)').
                      replace("_отсоединено", "")
                      )

        if 'SUB' in name:
            self.incorrect = True

        if 'LIB' in name:
            self.lib_file = True

        if ' ' in name and 'LIB' not in name:
            self.incorrect = True

        if not name.isprintable():
            self.incorrect = True

        # self.fullname = name.replace("_отсоединено", "")
        split_name = name.split('_')
        self.project = split_name[0]

        if len(split_name) > 4:
            self.stage = split_name[1]
            self.subpart = split_name[2]
            self.section = split_name[3]
            self.rvt = split_name[4]
        else:
            self.stage = str()
            self.subpart = str()

        if len(split_name) > 5:
            self.eir = split_name[4]
            self.rvt = split_name[5]

        if len(split_name) > 6:
            self.part = split_name[6]

        if len(self.project) > 6:
            self.incorrect = True
