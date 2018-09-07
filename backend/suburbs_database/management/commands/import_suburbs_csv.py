import csv
from django.core.management.base import BaseCommand
from ...models import SuburbData


class Command(BaseCommand):
    """
    Import a Australian suburbs CSV file as supplied by australiantownslist.com.
    Expected format:
    id  name    urban_area  state_code  state   postcode    type    latitude    longitude   elevation   population  area    local_government_area   timezone    bordering_location_ids
    1   Aarons Pass     NSW New South Wales 2850    Rural locality  -32.86328   149.80375   804 22  82.764  Mid-Western Regional (Area) Australia/Sydney    2468/2569/3488/3503/6325
    """
    def add_arguments(self, parser):
        """have to add this to use args in django 1.8+"""
        parser.add_argument('--file',
                            action="store",
                            dest="csv_file",
                            help="The filepath of the Australian suburbs csv")

    def handle(self, *args, **options):
        csv_file = options.get('csv_file')
        if not csv_file:
            raise Exception("CSV File required")

        with open(csv_file) as csvfile:
            reader = csv.DictReader(
                csvfile,
                fieldnames=[
                    'id',
                    'name',
                    'urban_area',
                    'state_code',
                    'state',
                    'postcode',
                    'type',
                    'latitude',
                    'longitude',
                    'elevation',
                    'population',
                    'area',
                    'local_government_area',
                    'timezone',
                    'bordering_location_ids',
                ]
            )
            for index, row in enumerate(reader):
                print(row)
                if index == 0:  # First row is header
                    continue
                self.handle_row(row)

    def handle_row(self, row):
        try:
            suburb = SuburbData.objects.get(
                id=row['id'],
            )
        except SuburbData.DoesNotExist:
            suburb = SuburbData(id=row['id'])

        for field, data in row.items():
            if field == 'bordering_location_ids' and data:
                data = [int(i) for i in data.split('/')]
                suburb.bordering_locations = data
            else:
                setattr(suburb, field, data)
        suburb.save()
