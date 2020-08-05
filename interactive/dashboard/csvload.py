import csv
from django.conf import settings
import os
from .save import load, save, export


def handle_uploaded_csv(f):
    with open(os.path.join(settings.BASE_DIR, 'dashboard/configfiles/input.csv'), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


pathto = os.path.join(settings.BASE_DIR, "dashboard/configfiles")


def read_csv():
    with open(os.path.join(pathto, "input.csv"), "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        rows = []
        for line in csv_reader:
            rows.append(line)
        columns = []
        for aa in rows[0]:
            columns.append([aa])
        for bb in rows[1]:
            i = rows[1].index(bb)
            columns[i].append(bb)

    dict = {}
    for col in columns:
        dict.update({col[0]: float(col[1])})

    species = {}
    conc = {}
    init = {}

    i = 1

    for key in dict:
        type = key.split('.')[0]
        name = key.split('.')[1]
        if type == 'CONC':
            title = "Species " + str(i)
            species.update({title: name})
            conc.update({title: dict[key]})
            i = i+1

        if type == 'ENV':
            init.update({name: dict[key]})

    load(species)
    save("formula")

    load(conc)
    save("value")

    load(init)
    save("conditions")

    export()




read_csv()



