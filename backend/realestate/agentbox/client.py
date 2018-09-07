"""
AgentBox API (v2) Connection client.
Connects to the AgentBox API to integrate with Wagtail/Django/Python and provide helper functions
to facilitate the build of AgentBox powered applicated.

Author: Jason Havenaar for TechEquipt Pty Ltd
Website: www.techequipt.com.au
Updated: 2018-04-25
"""

import os
import requests
from django.conf import settings


class AgentBoxException(Exception):
    """
    Created for brevity on where the issues lie
    """
    pass


class AgentBoxClient:
    """
    Base Agentbox connection client. All AgentBox API classes subclass this.
    Handles connection + authorisation
    """
    base_url = "https://api.agentboxcrm.com.au/"
    list_method = 'get'
    create_method = 'post'
    update_method = 'put'
    _key = None
    _client_id = None
    _session = None
    _version = "2"  # Api Requires version=2 in the parameters

    def __init__(self, *args, **kwargs):
        """
        We will look in 4 locations for the API Key / Client ID

        1. Kwargs passed to this object
        2. An "AgentBoxSettings" object
        3. Django settings AGENTBOX_API_KEY and AGENTBOX_CLIENT_ID
        4. Environment Variables AGENTBOX_API_KEY and AGENTBOX_CLIENT_ID
        """
        if kwargs.get('key') and kwargs.get('client_id'):
            self._key = kwargs['key']
            self._client_id = kwargs['client_id']
        else:
            # Wagtail setting Object
            try:
                from .models import AgentBoxSettings
                wagtail_setting_obj = AgentBoxSettings.objects.latest('pk')
                self._key = kwargs.get('key', wagtail_setting_obj.api_key)
                self._client_id = kwargs.get('key', wagtail_setting_obj.client_id)
            except (ImportError, AgentBoxSettings.DoesNotExist):
                pass

            # Django settings
            try:
                self._key = self._key or settings.AGENTBOX_API_KEY
                self._client_id = self._client_id or settings.AGENTBOX_CLIENT_ID
            except ValueError:
                pass

            # Environment variable
            self._key = self._key or os.environ.get('AGENTBOX_API_KEY')
            self._client_id = self._client_id or os.environ.get('AGENTBOX_CLIENT_ID')

        if not self._key:
            raise AgentBoxException("API Key required")

        self._session = requests.Session()
        self._session.headers.update({'X-API-Key': self._key, 'X-Client-ID': self._client_id})

    def build_url(self, endpoint):
        return self.base_url + endpoint + '?version=%s' % self._version

    def call(self, endpoint, method=list_method, params={}):
        """
        Handles the connection and authorisation to the API
        """
        full_url = self.build_url(endpoint)
        safe_methods = [self.list_method, self.update_method, self.create_method]

        if method not in safe_methods:
            raise AgentBoxException("Tried to use HTTP Method %s: Not Valid" % method)

        # We will clean the params to remove empty items
        params = {k: v for k, v in params.items() if v}

        request = getattr(self._session, method)
        response = request(full_url, params=params)
        response.raise_for_status()
        return response.json()


class AgentBoxListings(AgentBoxClient):
    """
    Listings provides for a read only API to query for listings and pull extra details
    on a specific listing. 
    """
    endpoint = 'listings'

    # 'Get' has a somewhat extensive list of includes that we will almost always want.
    default_get_include = "inspectionDates,relatedStaffMembers,externalLinks,documents,floorPlans,images"

    def list(self, page=1, limit=20, include="", orderBy="", order="", **filters):
        """
        Expected Parameters:
            include (relatedContacts|relatedStaffMembers|internalInformation|inspectionDates
                |mainImage|documents|mainDescription - accepts csv)
            orderBy (soldPrice|searchPrice|address|lastModified|firstCreated|listedDate|nextInspectionDate)
            order (ASC|DESC)

        Expected Filters:
            query (Text search on id/address/suburb/property name)
            officeId
            projectId
            memberId
            memberTeamId
            memberOfficeId
            memberRole
            memberWebDisplay (True|False - Filter properties by associated staff members web display)
            contactId
            contactRole
            unitNum
            lvNum (level number i.e in an apartment building)
            streetNum
            streetName
            type (Sale|Lease)
            status (Appraisal|Presentation|Pending|Available|Conditional|Unconditional|Settled|
                Leased|Withdrawn|Archived - accepts csv)
            marketingStatus (Not Listed|Available|Under Contract|Sold|Leased - Normal online status, accepts csv)
            hiddenListing (True|False)
            offMarketListing (True|False)
            propertyType (Residential|Rural|Commercial|Holiday|Business)
            propertyCategory (As per AgentBoxLookups.property_types)
            suburb
            region (As per AgentBoxLookups.regions)
            state
            incSurroundingSuburbs (True|False - Include surrounding suburbs from the suburb filter)
            listingMatchContactId (Match properties to contact(s), Supports multiple comma-separated values)
            listingMatchSearchRequirementId (Match properties to search requirement,
                Supports multiple comma-separated values)
            priceFrom, priceTo
            soldPriceFrom, soldPriceTo
            weeklyRentFrom, weeklyRentTo
            soldDateFrom, soldDateTo
            bedroomsFrom, bedroomsTo
            bathroomsFrom, bathroomsTo
            totalParkingFrom, totalParkingTo
            landAreaFrom, landAreaTo
            buildingAreaFrom, buildingAreaTo
            inspectionStartDateFrom, inspectionStartDateTo
            inspectionEndDateFrom, inspectionEndDateTo
            auctionDateFrom, auctionDateTo
            modifiedBefore, modifiedAfter
            createdBefore, createdAfter            
        """
        payload_filters = {'filter[%s]' % key: value for key, value in filters.items()}
        payload_filters.update({'page': page, 'limit': limit, 'include': include, 'orderBy': orderBy, 'order': order})
        return self.call(self.endpoint, params=payload_filters)

    def get(self, listingId, include=default_get_include):
        """
        Get all details for a listing. Possible "include" options are:
            default: see AgentBoxListings.default_get_include
            additional: appraisalDetails,comparableProperties,relatedContacts,internalInformation
        """
        if not listingId:
            raise AgentBoxException("AgentBoxListings.get - No listingId supplied")
        return self.call(self.endpoint + '/' + listingId, params={'include': include})


class AgentBoxContacts(AgentBoxClient):
    """
    Contacts are all people stored in the customers CRM system. They are attached to properties,
    have search requirements and include a log of their activities.
    This is a read-write API.
    """

    def list(self, page=1, limit=20, include="", orderBy="", order="", **filters):
        """
        Filter and query contact records.
        Possible "include" values:
            relatedStaffMembers,subscriptions,communicationRestrictions,permissions

        Expected filters include:
            General:
                createdBefore,createdAfter
                modifiedBefore,modifiedAfter
                type (Person|Business - the type of contact)
                status (Active|Archived|Do Not Contact|Unsubscribed|All)

            Contact Data (all accept csv):
                firstName
                lastName
                email
                companyName
                mobile
                homePhone
                workPhone
                contactClass
                address
                suburb
                postcode
                state
                subscription (Contacts associated to a subscription per AgentBoxLookups.subscription, accepts csv)
            
            Association:
                memberOfficeId (Contacts associated Office)
                memberTeamId (Contacts associated Staff Team)
                memberId (Contacts associated Staff member)
            
            Search Requirements:
                limitSearch (True|False - When True will exclude contacts without a search criteria)
                reqBuildingAreaFrom,reqBuildingAreaTo (Range for the contacts required Building Area)
                reqLandAreaFrom,reqLandAreaTo (Range for the contacts required Land Area)
                reqTotalParkingFrom,reqTotalParkingTo (Range for the contacts required number of car sports)
                reqBathroomsFrom,reqBathroomsTo (Range for the contacts required number of bathrooms)
                reqBedroomsFrom,reqBedroomsTo (Range for the contacts required number of bedrooms)
                reqPriceFrom,reqPriceTo (Range for the contacts insterested price range)
                reqFeature (Search Requirements features - accepts csv)
                reqRegion (Search Requirements Region - accepts csv)
                reqIncSurroundSuburbs (True|False - Include Surrounding suburbs)
                reqPostcode (Search Requirements Postcode)
                reqState (Search Requirements State)
                reqSuburb (Search Requirements Suburb)
                reqPropertyCategory (Search Requirements property category as per AgentBoxLookups.property_type)
                reqPropertyType (Residential|Rural|Commercial|Holiday|Business - Search Requirements)
                reqListingType (Sale|Lease - Search Requirements)
                reqMatchListingId (Match search requirements to a specific listing across all contacts)
        """
        payload_filters = {'filter[%s]' % key: value for key, value in filters}
        payload_filters.update({
            'page': page,
            'limit': limit,
            'include': include,
            'orderBy': orderBy,
            'order': order
        })
        return self.call(
            self.endpoint,
            params=payload_filters
        )

    def get(self, contactId, include=""):
        """
        Get details of a specific contact.
        Possible include values: relatedStaffMembers,searchRequirements,permissions
        """
        if not contactId:
            raise AgentBoxException('AgentBoxContacts.get: contactId required')
        return self.call(self.endpoint + '/' + contactId, params={'include': include})

    def create(self, title="", firstName="", lastName="", type="", customSalutation="",
               companyName="", jobTitle="", email="", mobile="", homePhone="", workPhone="",
               streetAddress={}, source="", comments="", attachedRelatedStaffMembers=[],
               contactClasses=[], subscriptions=[]):
        """
        Add a new contact. Important notes:
        type: Must be either "Person" or "Business"
        customSalutation (if supplied, will override the system generated salutation)
        source: Must be one of the values from AgentBoxLookups.contact_sources
        attachedRelatedStaffMembers: A list of staff member ID's. Will default view type to "Full Access"
        contactClasses: Must be valid values from GET AgentBoxLookups.contact_classes
        subscriptions: Must be valid values from AgentBoxLookups.subscription
        streetAddress: Expects:
            "streetAddress": {
                "address": "string",
                "suburb": "string",
                "state": "string",
                "country": "string",
                "postcode": "string"
            },
        """

        # Some basic validation
        if type not in ['Person', 'Business']:
            raise AgentBoxException('AgentBoxContacts.create: type not valid')

        payload_data = {
            'title': title,
            'firstName': firstName,
            'lastName': lastName,
            'type': type,
            'customSalutation': customSalutation,
            'companyName': companyName,
            'jobTitle': jobTitle,
            'email': email,
            'mobile': mobile,
            'homePhone': homePhone,
            'workPhone': workPhone,
            'streetAddress': streetAddress,
            'source': source,
            'comments': comments,
        }

        # Staff members are being forced as Full Access to we are munging some data
        if attachedRelatedStaffMembers:
            payload_data['attachedRelatedStaffMembers'] = [
                {'role': 'Full Access', 'id': i} for i in attachedRelatedStaffMembers
            ]

        # Contact Classes is CSV, but supplied as a list
        if contactClasses:
            payload_data['contactClasses'] = ",".join(contactClasses)

        # Subscriptions is CSV, but supplied as a list
        if subscriptions:
            payload_data['subscriptions'] = ",".join(subscriptions)

        return self.call(self.endpoint, method=self.create_method, params=payload_data)

    def update(self, contactId, title=None, firstName=None, lastName=None, type=None, status=None,
               customSalutation=None, companyName=None, jobTitle=None, email=None, mobile=None, homePhone=None,
               workPhone=None, streetAddress=None, source=None, comments=None, attachedRelatedStaffMembers=[],
               contactClasses=[], subscriptions=[]):
        """
        Update an existing contact record. All fields will only be sent if supplied (checking for 'not None') and
        contactClasses, attachedRelatedStaffMembers and subscriptions will be considered global overrides.
        See AgentBoxContact.create for field definitions.
        """
        if not contactId:
            raise AgentBoxException('AgentBoxContact.update: contactId is required')
        update_params = {}

        # Detail fields
        if title is not None:
            update_params['title'] = title
        if firstName is not None:
            update_params['firstName'] = firstName
        if lastName is not None:
            update_params['lastName'] = lastName
        if type is not None:
            # Type has validation
            if type not in ['Person', 'Business']:
                raise AgentBoxException('AgentBoxContacts.update: type not valid')
            update_params['type'] = type
        if status is not None:
            update_params['status'] = status
        if customSalutation:
            update_params['customSalutation'] = customSalutation
        if companyName is not None:
            update_params['companyName'] = companyName
        if companyName is not None:
            update_params['jobTitle'] = jobTitle
        if email is not None:
            update_params['email'] = email
        if mobile is not None:
            update_params['mobile'] = mobile
        if homePhone is not None:
            update_params['homePhone'] = homePhone
        if workPhone is not None:
            update_params['workPhone'] = workPhone
        if comments is not None:
            update_params['comments'] = comments

        # streetAddress is a dict and must have an 'address' key
        if streetAddress is not None and streetAddress.get('address'):
            update_params['streetAddress'] = streetAddress

        # attachedRelatedStaffMembers will be a global override
        if attachedRelatedStaffMembers:
            update_params['attachedRelatedStaffMembers'] = [
                {'role': 'Full Access', 'id': i} for i in attachedRelatedStaffMembers
            ]

        # Contact Classes is CSV, but supplied as a list
        if contactClasses:
            update_params['contactClasses'] = ",".join(contactClasses)

        # Subscriptions is CSV, but supplied as a list
        if subscriptions:
            update_params['subscriptions'] = ",".join(subscriptions)

        update_endpoint = self.endpoint + '/' + self.contactId
        return self.call(update_endpoint, method=self.update_method, params=update_params)


class AgentBoxSearchRequirements(AgentBoxClient):
    """
    Search requirements tie a user/contact to their preferred properties to search for.
    This is used for buyer matching and property alerts.
    """
    endpoint = "search-requirements"

    def list(self, page=1, limit=20, include="", orderBy="", order="", **filters):
        """
        List and Paginate through existing Search Requirements.
        Response Format: {
            "items": 0,
            "current": 0,
            "last": 0,
            "searchRequirements": [{}]
        }
        Expected filters:
            contactId,
            modifiedBefore,
            modifiedAfter,
            createdBefore,
            createdAfter
        """
        payload_filters = {'filter[%s]' % key: value for key, value in filters}
        payload_filters.update({
            'page': page,
            'limit': limit,
            'include': include,
            'orderBy': orderBy,
            'order': order
        })
        return self.call(
            self.endpoint,
            params=payload_filters
        )

    def get(self, id):
        """ Get a specific SearchRequirement by ID. """
        return self.call(self.endpoint + '/' + id)

    def create(self, contactId, name="", listingType="", propertyType="", propertyCategories="", price="", bedrooms="",
               bathrooms="", parking="", landArea="", buildingArea="", suburbs="", surroundingSuburbs="", regions=""):
        """
        Create a new search requirement / criteria and assign to an existing AgentBox Contact.
        contactId should be as per AgentBoxContacts results.
        """
        if not contactId:
            raise AgentBoxException("AgentBoxSearchRequirements.create: contactId is required")

        return self.call(
            self.endpoint,
            method=self.create_method,
            params={
                'contactId': contactId,
                'name': name,
                'listingType': listingType,
                'propertyType': propertyType,
                'propertyCategories': propertyCategories,
                'price': price,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'parking': parking,
                'landArea': landArea,
                'buildingArea': buildingArea,
                'suburbs': suburbs,
                'surroundingSuburbs': surroundingSuburbs,
                'regions': regions
            }
        )

    def update(self, searchRequirementId, name="", listingType="", propertyType="", propertyCategories="",
               price="", bedrooms="", bathrooms="", parking="", landArea="", buildingArea="", suburbs="",
               surroundingSuburbs="", regions=""):
        """
        Given an existing search requirment ID (from get/create responses), update the criteria
        """
        if not searchRequirementId:
            raise AgentBoxException("AgentBoxSearchRequirements.update: searchRequirementId is required")

        return self.call(
            self.endpoint,
            method=self.update_method,
            params={
                'searchRequirementId': searchRequirementId,
                'name': name,
                'listingType': listingType,
                'propertyType': propertyType,
                'propertyCategories': propertyCategories,
                'price': price,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'parking': parking,
                'landArea': landArea,
                'buildingArea': buildingArea,
                'suburbs': suburbs,
                'surroundingSuburbs': surroundingSuburbs,
                'regions': regions
            }
        )


class AgentBoxOffices(AgentBoxClient):
    """
    Offices are Real Estate Agencies that 1. Promote listings and 2. Have staff.
    This is a read only API to retrieve office details, and specific office details
    """
    endpoint = 'offices'

    def list(self, page=1, limit=20, include="mainImage", orderBy="", order="", **filters):
        """
        Retrieve and paginate through Office instances. include "mainImage" returns the main
        office image. AgentBox may have other "includes". Expected Filters:
            modifiedBefore
            modifiedAfter
            status (Active|Archived)
        """
        payload_filters = {'filter[%s]' % key: value for key, value in filters.items() if value}
        payload_filters.update({'page': page, 'include': include, 'limit': limit, 'orderBy': orderBy, 'order': order})
        return self.call(self.endpoint, params=payload_filters)

    def get(self, officeId):
        """
        Retrieve specific details of a given officeId, will by default add include="images" to return images in the
        response.
        """
        return self.call(self.endpoint + '/' + officeId, params={'include': 'images'})


class AgentBoxStaff(AgentBoxClient):
    """
    Staff are Real Estate Agents, Administrative staff and Other company members of an Office.
    This is a read only API to retrieve staff details and specific staff details
    """
    endpoint = "staff"

    def list(self, page=1, limit=20, include="mainImage", orderBy="", order="", **filters):
        """
        Retrieve and paginate through Office instances. include "mainImage" returns the main
        office image. AgentBox may have other "includes". Expected Filters:
            query (string search for id, name or email)
            officeid
            firstName
            lastName
            email
            status (active|all - all will return inactive staff)
            role (See AgentBoxLookUps.staff_role_types for valid options)
            webDisplay (flag to determine if the staff member should be publicly visible.
                AgentBoxLookUps.staff_web_display_types for valid options. Accepts CSV)
            teamId
        """
        payload_filters = {'filter[%s]' % key: value for key, value in filters.items()}
        payload_filters.update({'page': page, 'include': include, 'limit': limit, 'orderBy': orderBy, 'order': order})
        return self.call(self.endpoint, params=payload_filters)

    def get(self, memberId, include="images"):
        """
        Retrieve details of a given staff member by Id, will include images using the 'include' param by default
        """
        return self.call(self.endpoint + '/' + memberId, params={'include': include})


class AgentBoxLookUps(AgentBoxClient):
    """
    Various read only API's to pull in supplementary information. Each function will have
    a unique endpoint and requirements.
    """

    def regions(self, page=1, limit=20):
        """Returns a set of regions"""
        endpoint = 'regions'
        return self.call(endpoint, params={'page': page, 'limit': limit})

    def subscriptions(self, page=1, limit=20):
        """
        Returns a list of newsletter subscriptions which can be used to pass into the "subscribe" 
        endpoint to subscribe or unsubscribe contacts from specific mailing lists.
        """
        endpoint = 'subscription'
        return self.call(endpoint, params={'page': page, 'limit': limit})

    def property_types(self, page=1, limit=20):
        """Returns a set of property types"""
        endpoint = '/property-types'
        return self.call(endpoint, params={'page': page, 'limit': limit})

    def contact_classes(self, page=1, limit=20, query=""):
        """Returns a set of contact classes. Contact classes are types of contacts in the CRM"""
        endpoint = 'contact-classes'
        return self.call(endpoint, params={'page': page, 'limit': limit, 'filter[query]': query})

    def enquiry_types(self, page=1, limit=20):
        """
        Enquiry types are used to funnel contact enquiries into a specific channel (i.e Buyer vs. Vendor).
        Returns a list of current enquiry Types.
        Example Response:
            {
            "response": {
                "items": "7",
                "current": "1",
                "last": "1",
                "enquiryTypes": [
                    {
                    "id": "1",
                    "name": "General Enquiry"
                    },    
                    ...
                ]
            }
        """
        endpoint = 'enquiry-types'
        return self.call(endpoint, params={'page': page, 'limit': limit})

    def enquiry_sources(self, page=1, limit=20):
        """
        Enquiry Sources allow you to funnel a Contact isn't a specific souce (where it came from).
        Returns a list of current enquiry sources
        Example Response:
        {
        "response": {
            "items": "9",
            "current": "1",
            "last": "1",
            "enquirySources": [
            {
                "id": "1",
                "name": "Database"
            },
            {
                "id": "2",
                "name": "Domain.com.au"
            },
            {
                "id": "8",
                "name": "Website"
            },
            {
                "id": "9",
                "name": "Word Of Mouth"
            }
            ]
        }
        }
        """
        endpoint = 'enquiry-sources'
        return self.call(endpoint, params={'page': page, 'limit': limit})

    def enquiry_interest_levels(self, page=1, limit=20):
        """
        Contact funneling based on how interested they are.
        Returns a list of current interest levels.
        Example Response:
        {
        "response": {
            "items": "3",
            "current": "1",
            "last": "1",
            "enquiryInterestLevels": [
            {
                "id": "1",
                "name": "Hot"
            },
            {
                "id": "2",
                "name": "Warm"
            },
            {
                "id": "3",
                "name": "Cold"
            }
            ]
        }
        }
        """
        endpoint = 'enquiry-interest-levels'
        return self.call(endpoint, params={'page': page, 'limit': limit})

    def contact_sources(self, page=1, limit=20):
        """
        Contact funneling based on how the contact was made (i.e Phone vs. Website).
        Returns a list of contact sources.
        Example Response:
        {
        "response": {
            "items": "10",
            "current": "1",
            "last": "1",
            "contactSources": [
            {
                "id": "1",
                "name": "Phone Enquiry"
            },
            ...
            ]
        }
        }
        """
        endpoint = 'contact-sources'
        return self.call(endpoint, params={'page': page, 'limit': limit})

    def staff_web_display_types(self, page=1, limit=20):
        """
        Settings for a staff member regarding how they should display online.
        Returns a list of current web display types.
        Example response:
        {
        "response": {
            "items": "10",
            "current": "1",
            "last": "1",
            "staffWebDisplayTypes": [
            {
                "id": "1",
                "name": "My Listings"
            },
            {
                "id": "2",
                "name": "My Sold Properties"
            },
            ]
        }
        }
        """
        endpoint = 'staff-web-display-types'
        return self.call(endpoint, params={'page': page, 'limit': limit})

    def suburbs(self, page=1, limit=20, orderBy="", order="", **filters):
        """
        Query for and find australian suburbs including their details.
        Returns a list of filtered suburb datasets
        """
        endpoint = 'suburbs'
        payload_filters = {'filter[%s]' % key: value for key, value in filters}
        payload_filters.update({'page': page, 'limit': limit, 'orderBy': orderBy, 'order': order})
        return self.call(endpoint, params=payload_filters)
