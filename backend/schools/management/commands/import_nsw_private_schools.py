import csv
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from ...models import School


class Command(BaseCommand):
    """
    Import a NSW govt private schools CSV file
    """
    def add_arguments(self, parser):
        """have to add this to use args in django 1.8+"""
        parser.add_argument('--file',
                            action="store",
                            dest="csv_file",
                            help="The filepath of the NSW Private schools csv")

    def handle(self, *args, **options):
        csv_file = options.get('csv_file')
        if not csv_file:
            raise Exception("CSV File required")

        with open(csv_file, encoding='Latin-1') as csvfile:
            reader = csv.DictReader(
                csvfile,
                fieldnames=[
                    'ageID',
                    'head_campus_ageID',
                    'school_name',
                    'street',
                    'town_suburb',
                    'postcode',
                    'level_of_schooling',
                    'school_gender',
                    'sector',
                    'systemic',
                    'school_affiliation',
                    'diocese',
                    'sys_num',
                    'sys_desc',
                    'school _specialty_indicator',
                    'campus_level',
                    'school_url',
                    'lga',
                    'electorate_code',
                    'fed_electorate',
                    'SA3',
                    'SA4',
                    'ASGS_remoteness',
                    'latitude',
                    'longitude'
                ]
            )
            for index, row in enumerate(reader):
                if index == 0:  # First row is header
                    continue
                print(index)
                self.handle_row(row)

    def handle_row(self, row):
        try:
            school = School.objects.get(
                unique_id=row['ageID'],
            )
        except School.DoesNotExist:
            school = School(unique_id=row['ageID'])

        school.name = row['school_name']
        school.address = row['street']
        school.suburb = row['town_suburb']
        school.postcode = row['postcode']
        school.state = School.STATE_NSW
        school.location = Point(float(row['longitude']), float(row['latitude']))
        school.school_level = row['campus_level']
        school.school_type = School.SCHOOL_TYPE_PRIVATE
        school.save()
