

VEIKKAUSLIIGA_PATH = '../datafiles/finland/veikkausliiga'
YKKONEN_PATH = '../datafiles/finland/ykkönen'

for inputpath in (VEIKKAUSLIIGA_PATH, YKKONEN_PATH):
    for filename in [f for f in listdir(inputpath) if isfile(join(inputpath, f))]:
        print filename

    
