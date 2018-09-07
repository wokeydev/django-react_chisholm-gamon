import csv
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from ...models import School


class Command(BaseCommand):
    """
    Import a NSW govt public schools CSV file
    """
    def add_arguments(self, parser):
        """have to add this to use args in django 1.8+"""
        parser.add_argument('--file',
                            action="store",
                            dest="csv_file",
                            help="The filepath of the NSW Public schools csv")

    def handle(self, *args, **options):
        csv_file = options.get('csv_file')
        if not csv_file:
            raise Exception("CSV File required")

        with open(csv_file, encoding='Latin-1') as csvfile:
            reader = csv.DictReader(
                csvfile,
                fieldnames=[
                    'school_code',
                    'AgeID',
                    'school_name',
                    'street',
                    'town_suburb',
                    'postcode',
                    'student_number',
                    'indigenous_pct',
                    'lbote_pct',
                    'ICSEA_Value',
                    'level_of_schooling',
                    'selective_school',
                    'opportunity_class',
                    'school_specialty_type',
                    'school_subtype',
                    'support_classes',
                    'preschool_ind',
                    'distance_education',
                    'intensive_english_centre',
                    'school_gender',
                    'phone',
                    'school_email',
                    'fax',
                    'late_opening_school',
                    'date_1st_teacher',
                    'lga',
                    'electorate',
                    'fed_electorate',
                    'operational_directorate',
                    'principal_network',
                    'facs_district',
                    'local_health_district',
                    'aecg_region',
                    'ASGS_remoteness',
                    'latitude',
                    'longitude',
                    'date_extracted'
                ]
            )
            for index, row in enumerate(reader):
                if index == 0:  # First row is header
                    continue
                self.handle_row(row)
                print(index)

    def handle_row(self, row):
        try:
            school = School.objects.get(
                unique_id=row['AgeID'],
            )
        except School.DoesNotExist:
            school = School(unique_id=row['AgeID'])
        school.name = row['school_name']
        school.address = row['street']
        school.suburb = row['town_suburb']
        school.postcode = row['postcode']
        school.state = School.STATE_NSW
        school.location = Point(float(row['longitude']), float(row['latitude']))
        school.school_level = row['level_of_schooling']
        school.school_type = School.SCHOOL_TYPE_PUBLIC
        school.save()
