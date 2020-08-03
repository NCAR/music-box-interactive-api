import csv
from django.conf import settings
import os
# #
def handle_uploaded_csv(f):
   with open(os.path.join(settings.BASE_DIR, 'dashboard/configfiles/species.csv'), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
#
#
# #pathto = os.path.join(settings.BASE_DIR, "dashboard/configfiles")
#
#
# def read_csv():
#     with open("/Users/simonthomas/music-box-interactive/interactive/dashboard/configfiles/species.csv", "r") as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=',')
#         for lines in csv_reader:
#             print(lines)
#
#
#
