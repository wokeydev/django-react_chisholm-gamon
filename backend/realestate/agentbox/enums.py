from realestate.listings import enums as listing_enums

WEBSITE_MARKETING_STATUS_CREATE = [
    # Valid marketingStatus values for new listings
    'Available',
    'Under Contract',
    'Sold',
    'Leased'
]

MARKETING_STATUS_MAP = {
    'Available': listing_enums.STATUS_CURRENT,
    'Sold': listing_enums.STATUS_SOLD,
    'Leased': listing_enums.STATUS_LEASED,
    'Not Listed': listing_enums.STATUS_WITHDRAWN
}

DEFAULT_MARKETING_STATUS = 'Not Listed'
UNDER_OFFER_MARKETING_STATUS = 'Under Contract'


FEATURE_NAME_CLEANUP = {
    'loungeRooms': 'Lounge Rooms',
    'toilets': 'Toilets',
    'studies': 'Studies',
    'pools': 'Pool',
    'garages': 'Garages',
    'carPorts': 'Car Ports',
    'carSpaces': 'Car Spaces',
}
