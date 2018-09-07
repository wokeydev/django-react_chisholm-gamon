from itertools import zip_longest
from django.contrib.gis.geos import Point
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from wagtail.core.models import PageRevision
from realestate.offices.models import OfficePage, OfficeIndexPage
from realestate.agents.models import (AgentPage, AgentIndexPage, AgentCategory,
                                      AgentPageCategoryChoice, AgentPageOffice)
from realestate.listings.models import (PropertyListing, PropertyCategory, PropertyFeature, ListingAgent,
                                        Inspection, ListingLink, ListingImage, ListingFloorplan)
from realestate.listings import enums as listing_enums
from cms.utils import wagtail_image_from_url
from .client import (AgentBoxListings, AgentBoxContacts, AgentBoxSearchRequirements,
                     AgentBoxOffices, AgentBoxStaff, AgentBoxLookUps, AgentBoxException)
from .models import AgentBoxUpdateMeta
from . import enums


def import_agentpoint_offices(since=None, refresh=False):
    """
    Contact the AgentBox API and import office records, creating realestate.offices.OfficePage
    objects. Will update existing pages based on OfficePage.source_id.

    params:
        since (datetime): Request Office records updated since this
        refresh (bool): Fully refresh all records.
        Note: If both since and refresh are False(y) we will use the last updated from AgentBoxUpdateMeta.last_updated_offices

    Workflow:
        1. Determine update since date
        2. List offices
        3. Get each office
        4. Create or update record
    """
    ALL_OFFICES_LIMIT = 150

    try:
        meta, _ = AgentBoxUpdateMeta.objects.get_or_create()
    except AgentBoxUpdateMeta.MultipleObjectsReturned:
        raise AgentBoxException('import_agentpoint_offices: Too Many AgentBoxUpdateMeta')

    if not since and not refresh:
        since = meta.last_updated_offices

    offices_client = AgentBoxOffices()
    offices_list_data = offices_client.list(
        limit=ALL_OFFICES_LIMIT,
        modifiedAfter=since.isoformat() if since else None
    )
    offices_data = []
    for office_list_data in offices_list_data['response'].get('offices', []):
        office_data = offices_client.get(office_list_data['id'])
        if office_data['response'].get('office'):
            offices_data.append(office_data['response']['office'])

    for office_data in offices_data:
        _process_office_data(office_data)


def _process_office_data(office_data={}):
    """
    Process the single offices data, updating or creating the page if needed.
    Includes saving images
    """
    try:
        office_page = OfficePage.objects.get(source_id=office_data['id'])
    except OfficePage.DoesNotExist:
        office_page = OfficePage(source_id=office_data['id'])
    except OfficePage.MultipleObjectsReturned:
        raise AgentBoxException('import_agentpoint_offices: Multiple OfficePage of ID %s' % office_data['id'])

    mapped_fields = {
        # Mapping of AgentBox field to OfficePage field

        'name': 'office_name',
        'email': 'email',
        'phone': 'phone',
        'fax': 'fax',
    }

    for ab_field, page_field in mapped_fields.items():
        setattr(office_page, page_field, office_data.get(ab_field))

    #  title and office_name are the same so we will just copy it.
    office_page.title = office_page.office_name

    # Handle Address
    address_data = office_data.get('address', {})
    if address_data.get('streetAddress'):
        office_page.address = address_data['streetAddress']
    if address_data.get('suburb'):
        office_page.suburb = address_data['suburb']
    if address_data.get('state'):
        office_page.state = address_data['state']
    if address_data.get('postcode'):
        office_page.postcode = address_data['postcode']

    # Handle Social Accounts - We store handles/names on some fields to will need to munge
    for link in office_data.get('externalLinks'):
        if link['type'] == 'facebook':
            office_page.facebook_url = link['link']
        elif link['type'] == 'twitter':
            # We just want the handle
            office_page.twitter_handle = link['link'].split('/')[-1]
        elif link['type'] == 'linkedin':
            office_page.linkedin_url = link['link']
        elif link['type'] == 'instagram':
            office_page.instagram_handle = link['link'].split('/')[-2]
        elif link['type'] == 'youtube':
            office_page.youtube_url = link['link']

    # Handle Lat/Lng
    if office_data.get('location'):
        office_page.latitude = office_data['location']['lat'][:9]
        office_page.longitude = office_data['location']['long'][:9]

    # TODO: Images into OfficePage.featured_image

    # If this is a new page (OfficePage.pk is None) we need to
    # Put it in the OfficeIndex
    if office_page.pk is None:
        index = OfficeIndexPage.objects.latest('pk')
        index.add_child(instance=office_page)

    office_page.save()
    office_page.save_revision().publish()


def import_agentpoint_staff(since=None, refresh=None):
    """
    Contact the AgentBox API and import staff records, creating realestate.offices.AgentPage
    objects. Will update existing pages based on AgentPage.source_id.

    params:
        since (datetime): Request Office records updated since this
        refresh (bool): Fully refresh all records.
        Note: If both since and refresh are False(y) we will use the last updated from AgentBoxUpdateMeta.last_updated_staff

    Workflow:
        1. Determine update since date
        2. List staff
        3. Get each staff
        4. Create or update record
    """
    ALL_STAFF_LIMIT = 150

    try:
        meta, _ = AgentBoxUpdateMeta.objects.get_or_create()
    except AgentBoxUpdateMeta.MultipleObjectsReturned:
        raise AgentBoxException('import_agentpoint_offices: Too Many AgentBoxUpdateMeta')

    if not since and not refresh:
        since = meta.last_updated_staff

    staff_client = AgentBoxStaff()
    staff_list_data = staff_client.list(
        limit=ALL_STAFF_LIMIT,
        modifiedAfter=since.isoformat() if since else None
    )

    staffs_data = []
    for staff_list_data in staff_list_data['response'].get('staffMembers', []):
        staff_data = staff_client.get(staff_list_data['id'])
        if staff_data['response'].get('staffMember'):
            staffs_data.append(staff_data['response']['staffMember'])

    for staff_data in staffs_data:
        _process_staff_data(staff_data)


def _process_staff_data(staff_data={}):
    """
    Process the single staff data, updating or creating the page if needed.
    Includes saving images.
    AgentPage will only be saved/created if the staff is marked webDisplay as per AgentBoxSettings.staff_webdisplay and
    an active value of True
    TODO: webDisplay Handling
    """
    try:
        agent_page = AgentPage.objects.get(source_id=staff_data['id'])
        if staff_data['status'] != 'Active':
            agent_page.delete()
            return
    except AgentPage.DoesNotExist:
        agent_page = AgentPage(source_id=staff_data['id'])
        if staff_data['status'] != 'Active':
            return
    except AgentPage.MultipleObjectsReturned:
        raise AgentBoxException('import_agentpoint_offices: Multiple OfficePage of ID %s' % office_data['id'])

    mapped_fields = {
        'firstName': 'name_short',
        'jobTitle': 'job_title',
        'email': 'email',
        'mobile': 'phone',
        'phone': 'office_phone',
        'profile': 'about_me',
        'profileVideo': 'video_url'
    }
    for ab_field, page_field in mapped_fields.items():
        setattr(agent_page, page_field, staff_data.get(ab_field))

    # Page title is First + Last Name
    agent_page.title = " ".join([agent_page.name_short, staff_data['lastName']]).strip()

    # The rest of the data is FK Linked, so we want to save the object now
    # If this is a new page (AgentPage.pk is None) we need to
    # Put it in the AgentIndex
    if agent_page.pk is None:
        index = AgentIndexPage.objects.latest('pk')
        index.add_child(instance=agent_page)
    agent_page.save()

    # role's are agent categories
    if staff_data.get('role'):
        category, _ = AgentCategory.objects.get_or_create(category_name=staff_data['role'])
        AgentPageCategoryChoice.objects.get_or_create(
            sort_order=0,
            page=agent_page,
            category=category
        )

    # Office is based on Source ID
    if staff_data.get('officeId') and OfficePage.objects.filter(source_id=staff_data['officeId']):
        AgentPageOffice.objects.get_or_create(
            sort_order=0,
            office=OfficePage.objects.get(source_id=staff_data['officeId']),
            offices=agent_page
        )

    # First image will be the profile image
    if staff_data.get('images'):
        wagtail_image = wagtail_image_from_url(staff_data['images'][0].get('url'))
        agent_page.profile_image = wagtail_image

    # Once all the extra data is there we can publish the revision
    agent_page.save_revision().publish()


def import_agentpoint_listings(since=None, refresh=None):
    """
    Contact the AgentBox API and import Listings records, creating realestate.listings.PropertyListing
    objects. Will update existing listings based on PropertyListing.uniqueId.

    params:
        since (datetime): Request Listings records updated since this
        refresh (bool): Fully refresh all records.
        Note: If both since and refresh are False(y) we will use the last updated from
        AgentBoxUpdateMeta.last_updated_listings

    Workflow:
        1. Determine update since date
        2. List listings
        3. Get each listing
        4. Create or update record
    """

    try:
        meta, _ = AgentBoxUpdateMeta.objects.get_or_create()
    except AgentBoxUpdateMeta.MultipleObjectsReturned:
        raise AgentBoxException('import_agentpoint_offices: Too Many AgentBoxUpdateMeta')

    if not since and not refresh:
        since = meta.last_updated_listings

    client = AgentBoxListings()
    list_data = client.list(
        modifiedAfter=since.isoformat() if since else None
    )
    listings_data = []
    # Listings will likely need pagination - so we will build up the list
    listings_data += list_data['response'].get('listings', [])
    page = 1
    while list_data.get('last') and list_data['current'] != list_data['last']:
        # Current Page and Total Pages in response
        page += 1
        list_data = client.list(
            page=page,
            modifiedAfter=since.isoformat() if since else None
        )
        listings_data += list_data.get('listings', [])

    detailed_listing_data = []
    for listings_list_data in listings_data:
        listing_data = client.get(listings_list_data['id'])
        if listing_data['response'].get('listing'):
            detailed_listing_data.append(listing_data['response']['listing'])

    for listing_data in detailed_listing_data:
        _process_listing_data(listing_data)


def _process_listing_data(listing_data={}):
    if not listing_data.get('id') and listing_data.get('officeId'):
        raise AgentBoxException('import_agentpoint_listings: Missing required id or officeId')
    try:
        listing = PropertyListing.objects.get(
            uniqueID=listing_data['id'],
            agentID=listing_data['officeId']
        )
    except PropertyListing.DoesNotExist:
        listing = PropertyListing(
            uniqueID=listing_data['id'],
            agentID=listing_data['officeId']
        )

    # We don't want not-active new listings
    if not listing.pk and listing_data.get('marketingStatus', '') not in enums.WEBSITE_MARKETING_STATUS_CREATE:
        print("Not active new listing (%s), skipping (ID: %s)" % (listing_data['marketingStatus'], listing_data['id']))
        return

    # 1-1 match fields
    mapped_fields = {
        'auctionDate': 'auction_date',
        'displayPrice': 'priceView',
        'searchPrice': 'price',
        'soldDate': 'soldDetails_date',
        'soldPrice': 'soldPrice',
        # 'soldPriceConfidential': 'soldDetails_price_display' - it's actually the reverse
        'bedrooms': 'bedrooms',
        'bathrooms': 'bathrooms',
        'totalParking': 'parking',
        'energyRating': 'buildingDetails_energyRating',
        'mainHeadline': 'headline',
        'mainDescription': 'description',
        'lastModified': 'modTime',
        'authority': 'authority',

    }

    for ab_field, listing_field in mapped_fields.items():
        setattr(listing, listing_field, listing_data.get(ab_field))

    # Status Handling: marketingStatus is our online status - and we can flag offMarketListings too
    if listing_data.get('marketingStatus', enums.DEFAULT_MARKETING_STATUS) in enums.MARKETING_STATUS_MAP:
        listing.status = enums.MARKETING_STATUS_MAP[listing_data['marketingStatus']]
    if listing_data.get('marketingStatus') == enums.UNDER_OFFER_MARKETING_STATUS:
        listing.underOffer = True
    if listing_data.get('offMarketListing'):
        listing.status = listing_enums.STATUS_PREMARKET

    # Address and Type are in 'property'
    if not listing_data.get('property'):
        raise AgentBoxException('import_agentpoint_listings: Badly formed listing')

    listing.property_class = listing_data['property']['type'].lower()
    listing.listing_type = listing_data['type'].lower()

    # AgentBox don't differential between Residential Sale vs. Lease, so we fix
    if listing.property_class == listing_enums.PROPERTY_CLASS_RESIDENTIAL and \
            listing.listing_type == listing_enums.LISTING_TYPE_LEASE:
        listing.property_class = listing_enums.PROPERTY_CLASS_RENTAL

    if listing_data['property'].get('address'):
        # No address - can't move forward
        raise AgentBoxException('import_agentpoint_listings: Badly formed listing (no address)')

    property_data = listing_data['property']

    # Location information
    address_data = property_data['address']
    listing.address_street = address_data.get('streetName', '')
    listing.address_subNumber = address_data.get('unitNum', address_data.get('logNum', ''))
    listing.address_suburb = address_data.get('suburb', '')
    listing.address_state = address_data.get('state', '')
    listing.address_postcode = address_data.get('postcode', '')
    listing.address_country = address_data.get('country', '')

    # Mapping
    if property_data.get('location'):
        listing.location = Point(
            float(property_data['location'].get('long', 0)),
            float(property_data['location'].get('lat', 0))
        )
    else:
        pass  # TODO: Geocode if no lat/lng supplied?

    # area
    if property_data.get('buildingArea'):
        listing.buildingDetails_area = property_data['buildingArea'].get('value')
        listing.buildingDetails_area_unit = property_data['buildingArea'].get('unit')

    if property_data.get('landArea'):
        listing.buildingDetails_area = property_data['landArea'].get('value')
        listing.buildingDetails_area_unit = property_data['landArea'].get('unit')

    if property_data.get('frontage'):
        listing.buildingDetails_area = property_data['frontage'].get('value')
        listing.buildingDetails_area_unit = property_data['frontage'].get('unit')

    if property_data.get('newConstruction'):
        listing.buildingDetails_newlyBuilt = True
        listing.newConstruction = True

    # The rest of the fields need the listing to exist - so we'll save now
    listing.save()

    # Category
    if property_data.get('category'):
        #  AgentBox only sends 1 category - we will assume the first
        try:
            category = PropertyCategory.objects.get(sort_order=0, listing=listing)
        except PropertyCategory.DoesNotExist:
            category = PropertyCategory(sort_order=0, listing=listing)
        if category != property_data['category']:
            category.name = property_data['category']
            category.save()

    # Features
    property_data_features = [
        # These are standalone fields in the response, but will be ListingFeature objects
        'loungeRooms',
        'toilets',
        'studies',
        'pools',
        'garages',
        'carPorts',
        'carSpaces',
    ]
    if property_data.get('features'):
        # Comes in as a csv string
        property_data_features += property_data['features'].split(',')

    for feature in property_data_features:
        if property_data.get(feature):
            # We have nice name versions in enums - clean or use as is
            clean_feature = enums.FEATURE_NAME_CLEANUP.get(feature, feature)
            try:
                db_feature = PropertyFeature.objects.get(
                    listing=listing,
                    name=clean_feature
                )
            except PropertyFeature.DoesNotExist:
                db_feature = PropertyFeature(
                    sort_order=0,
                    listing=listing,
                    name=clean_feature
                )

            if db_feature.value != property_data[feature]:
                db_feature.value = property_data[feature]
                db_feature.save()

    # Agents - we will call based on source_id on AgentPage
    if listing_data.get('relatedStaffMembers'):
        # We want to remove any extra agents and make sure these are assigned
        for index, staff_data in enumerate(listing_data['relatedStaffMembers']):
            if staff_data['webDisplay'] is False:
                # Agent atteched internally but not on advertising
                continue
            try:
                agent = ListingAgent.objects.get(listing=listing, sort_order=index)
            except ListingAgent.DoesNotExist:
                agent = ListingAgent(listing=listing, sort_order=index)

            page = None
            if 'staffMember' in staff_data and staff_data['staffMember'].get('id'):
                try:
                    page = AgentPage.objects.get(source_id=staff_data['staffMember']['id'])
                except AgentPage.DoesNotExist:
                    # Agent not in DB, skip
                    continue

            if page and page.pk != agent.agent_id:
                agent.agent = page
                agent.save()

    # TODO: Documents
    """
    3 scenarios to account for, 2 with actions:
        1. images tag is missing - Don't edit the photos
        2. images tag exists but is empty - delete all photos
        3. Images tag has content - check and update the existing data

    This is also the same for Floorplans
    """
    existing_images = ListingImage.objects.filter(listing=listing)
    if 'images' in listing_data:
        if listing_data['images'] is None or listing_data['images'] == []:
            # Remove all
            existing_images.delete()
        else:
            _process_listing_media(listing, listing_data['images'], existing_images, 'images')

    existing_floorplans = ListingFloorplan.objects.filter(listing=listing)
    if 'floorPlans' in listing_data:
        if listing_data['floorPlans'] is None or listing_data['floorPlans'] == []:
            # Remove all
            existing_floorplans.delete()
        else:
            _process_listing_media(listing, listing_data['floorPlans'], existing_floorplans, 'floorPlans')


def _process_listing_media(listing, media_datas, existing_records_qs, media_type='images'):
    """
    Check our existing records and update accordingly. For images and floorplans
    NOTE: Floorplans don't have a modified time - so will always update. To discuss with Agentbox.
    """
    for index, record, media in enumerate(zip_longest(existing_records_qs, media_datas)):
        if not media:
            # The new images have less than the old, remove the extras
            record.delete()

        if 'url' not in media:
            raise AgentBoxException('Processing Media: URL not found\n %s' % media)

        # See if the mod time on the imported data is newer than the existing
        try:
            media_mod_time = parse_datetime(media['lastModified'])
        except ValueError:
            media_mod_time == timezone.now()
        if record and record.external_modtime < media_mod_time:
            # Our record is older, update
            setattr(record, record.media_field, wagtail_image_from_url(media['url']))
            record.external_modtime = media_mod_time
            record.save()
        elif not record:
            # Create the new image
            media_obj = ListingImage(listing=listing, sort_order=index)
            setattr(media_obj, media_obj.media_field, wagtail_image_from_url(media['url']))
            media_obj.save()
        else:
            # Our record is newer or same, so skip
            continue


def _process_listing_docs(listing, doc_datas, existing_records_qs):
    """
    TODO:
    Verify, and save documents for a listing. Does not have modified times - but supplies an ID.
    """
    pass