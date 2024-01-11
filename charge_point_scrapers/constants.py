# Info marker ids
FULL_ADDRESS_MARKER = 550
DATE_CREATED_MARKER = 511
PARKING_FEE_MARKER = 560
CHARGING_FEE_MARKER = 568
LOCATION_URL_MARKER = 547

# LAT/LONG limits for UK map
WESTERN_MOST_LONGITUDE_UK = -1
# WESTERN_MOST_LONGITUDE_UK = -8
# EASTERN_MOST_LONGITUDE_UK = 2
EASTERN_MOST_LONGITUDE_UK = -1
# NORTHERN_MOST_LATITUDE_UK = 60
NORTHERN_MOST_LATITUDE_UK = 50
# SOUTHERN_MOST_LATITUDE_UK = 49
SOUTHERN_MOST_LATITUDE_UK = 49

BOUNDING_BOX_FILTER_URL = 'https://api.zap-map.io/locations/v1/search/bounding-box?' \
                          'latitude={latitude}&longitude={longitude}' \
                          '&category=B_AND_B,CAMPSITE_CARAVAN_PARK,HOLIDAY_HOMES,HOSTEL,HOTEL,BEST_WESTERN,' \
                          'HILTON,HOLIDAY_INN,IBIS,MARRIOTT,NOVOTEL,HOTEL_OTHER,PREMIER_INN,RADISSON_BLU,TRAVELODGE,' \
                          'ACCOMMODATION_OTHER,ACCOMMODATION,AUDI,BMW,CITROEN,FIAT,FORD,HONDA,HYUNDAI,KIA,MERCEDES,' \
                          'MG_MOTORS,MITSUBISHI,NISSAN,DEALERSHIP_OTHER,DEALERSHIP_BRAND_OTHER,PEUGEOT,RENAULT,' \
                          'SHOWROOM,SKODA,TESLA,TOYOTA,VAUXHALL,VOLKSWAGEN,VOLVO,DEALERSHIP,HOME,GP_OTHER,HOSPITAL,' \
                          'NUFFIELD_HEALTH,HOSPITAL_OTHER,HEALTH_SERVICES_OTHER,HEALTH_SERVICES,ENTERTAINMENT,' \
                          'GALLERY_MUSEUM,HERITAGE_PROPERTY,ENGLISH_HERITAGE,NATIONAL_TRUST,HERITAGE_PROPERTY_OTHER,' \
                          'LANDMARK,LEISURE_CENTRE_GYM,BANNATYNE,DAVID_LLOYD,LEISURE_CENTRE_GYM_OTHER,MARINA,' \
                          'LEISURE_OTHER,PLACE_OF_WORSHIP,RACECOURSE,RECREATIONAL_PARK,SPORTS_FACILITY,THEATRE,' \
                          'THEME_PARK,WILDLIFE_PARK,LEISURE,HIGH_STREET,ON_STREET_OTHER,RESIDENTIAL,ON_STREET,' \
                          'OTHER,PARK_AND_RIDE,COMMUNITY_CENTRE,COUNCIL_OFFICES_OTHER,LIBRARY,PUBLIC_SERVICES_OTHER,' \
                          'PUBLIC_SERVICES,BURGER_KING,COSTA,DOMINOS,HARVESTER,KFC,MARSTONS,MCDONALDS,' \
                          'MILLER_AND_CARTER,RESTAURANT_PUB_CAFE_OTHER,STARBUCKS,TOBY_CARVERY,RESTAURANT_PUB_CAFE,' \
                          'B_AND_Q,IKEA,INTU,RETAIL_CAR_PARK_OTHER,RETAIL_CAR_PARK,COLLEGE_OTHER,NURSERY,' \
                          'EDUCATION_OTHER,SCHOOL,UNIVERSITY,EDUCATION,AIRPORT,BUS_STATION,' \
                          'TRAVEL_INTERCHANGE_CAR_PARK,FERRY_TERMINAL,TRAVEL_INTERCHANGE_OTHER,TRAIN_STATION,' \
                          'TRAVEL_INTERCHANGE&page={page}'

ZAP_MAP_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    "Host": "api.zap-map.io",
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip,deflate,br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Sec-GPC': '1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Origin': 'https://map.zap-map.com',
    'Referer': 'https://map.zap-map.com/'
}

CHARGE_POINT_DETAILS_ENDPOINT = 'https://api.zap-map.io/locations/v1/location/{uuid}'
