import csv

def handle_uploaded_csv(f):
    with open('configfiles/species.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

#with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/configfiles/species.csv', newline='') as file:

