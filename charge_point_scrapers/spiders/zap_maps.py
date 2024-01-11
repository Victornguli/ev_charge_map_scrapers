import json
from pathlib import Path

import scrapy
from scrapy import Request
from scrapy.http import Response


from charge_point_scrapers.constants import (
    WESTERN_MOST_LONGITUDE_UK,
    EASTERN_MOST_LONGITUDE_UK,
    NORTHERN_MOST_LATITUDE_UK,
    SOUTHERN_MOST_LATITUDE_UK,
    BOUNDING_BOX_FILTER_URL,
    ZAP_MAP_REQUEST_HEADERS,
    CHARGE_POINT_DETAILS_ENDPOINT
)
from charge_point_scrapers.utils import copy_headers, request_zap_auth_token, parse_date


class ZapMapsSpider(scrapy.Spider):
    name = "zap_maps"
    allowed_domains = ['api.zap-map.io', 'auth.zap-map.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'charge_point_scrapers.pipelines.ZapMapsPipeline': 300,
            'charge_point_scrapers.pipelines.ZapMapsOutPipeline': 99999,
        }
    }
    auth_headers = {}

    def start_requests(self):
        self.scraped_points = {}
        root_dir = Path(__file__).parent.parent.parent
        feeds = self.settings.get('FEEDS')
        feed_paths = list(feeds.keys())
        jsonl_feed_path = None
        if feed_paths and feeds[feed_paths[0]]['format'] == 'jl':
            jsonl_feed_path = root_dir / feed_paths[0]

        if jsonl_feed_path and jsonl_feed_path.exists():
            self.logger.info(f"Found previous feed export at: {jsonl_feed_path}")
            with open(jsonl_feed_path, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    line_data = json.loads(line)
                    self.scraped_points[line_data['uuid']] = 1

        self.logger.info(f"Loaded {len(self.scraped_points.keys())} scraped points")

        yield request_zap_auth_token(callback=self.top_level_search)

    def top_level_search(self, response):
        token = json.loads(response.text)['access_token'].strip()
        self.auth_headers = copy_headers(
            ZAP_MAP_REQUEST_HEADERS,
            {'Authorization': f"Bearer {token}", 'TE': 'trailers'}
        )
        for latitude in range(SOUTHERN_MOST_LATITUDE_UK, NORTHERN_MOST_LATITUDE_UK + 1):
            for longitude in range(WESTERN_MOST_LONGITUDE_UK, EASTERN_MOST_LONGITUDE_UK + 1):
                lat_cor, long_cor = f'{latitude}.0', f'{longitude}.0'
                yield Request(
                    BOUNDING_BOX_FILTER_URL.format(latitude=lat_cor, longitude=long_cor, page=1),
                    headers=self.auth_headers,
                    callback=self.top_level_boundary_search,
                    cb_kwargs={'latitude': lat_cor, 'longitude': long_cor},
                    dont_filter=True
                )

    def top_level_boundary_search(
            self,
            response: Response,
            latitude: str,
            longitude: str
    ):
        """
        Extract page_data from top level filters which is upto 250 total records per lat:long pair
        If next page exists(current_page < last_page) then follow the next page upto the end, yielding each point found
        in results

        If total top level count > 250 then proceed to do a lower level filter using the same strat above.
        :return:
        """
        json_res = json.loads(response.text)
        page_data = json_res['data']
        top_lvl_total = json_res['meta']['total']
        last_page = json_res['meta']['last_page']
        current_page = json_res['meta']['current_page']

        if top_lvl_total <= 250:
            for point in page_data:
                if point['uuid'] not in self.scraped_points:
                    yield Request(
                        CHARGE_POINT_DETAILS_ENDPOINT.format(uuid=point['uuid']),
                        headers=self.auth_headers,
                        callback=self.parse_charge_point_details,
                        cb_kwargs={'date_created': point['created_at']}
                    )

            if current_page < last_page:
                yield Request(
                    BOUNDING_BOX_FILTER_URL.format(latitude=latitude, longitude=longitude, page=current_page+1),
                    headers=self.auth_headers,
                    callback=self.top_level_boundary_search,
                    cb_kwargs={'latitude': latitude, 'longitude': longitude}
                )
        else:
            for i in range(0, 10):
                int_lat, int_long = int(float(latitude)), int(float(longitude))
                low_lvl_lat = f'{int_lat}.{i}0'
                neg_adjusted = int_long
                if int_long < 0:
                    if int_long == -1:
                        # At -1, longitude filters will be from -1.00 to -0.90 with -1.0 being exclusive
                        # Since we can't sign the int 0 set neg_adjusted as a string -0
                        neg_adjusted = '-0'
                    else:
                        neg_adjusted += 1

                    yield Request(
                        BOUNDING_BOX_FILTER_URL.format(latitude=low_lvl_lat, longitude=f'{int_long}.00', page=1),
                        headers=self.auth_headers,
                        callback=self.low_level_boundary_search,
                        cb_kwargs={'latitude': low_lvl_lat, 'longitude': f'{int_long}.00'},
                        dont_filter=True
                    )

                for j in range(1, 10):
                    low_lvl_long = f'{neg_adjusted}.{j}0'
                    yield Request(
                        BOUNDING_BOX_FILTER_URL.format(latitude=low_lvl_lat, longitude=low_lvl_long, page=1),
                        headers=self.auth_headers,
                        callback=self.low_level_boundary_search,
                        cb_kwargs={'latitude': low_lvl_lat, 'longitude': low_lvl_long},
                        dont_filter=True
                    )

    def low_level_boundary_search(
            self,
            response: Response,
            latitude: str,
            longitude: str,
    ):
        """
        Low level filter/search if top level count > 250.
        Uses same strategy as search_latitude_boundary to filter down pages.
        """
        json_res = json.loads(response.text)
        page_data = json_res['data']
        last_page = json_res['meta']['last_page']
        current_page = json_res['meta']['current_page']
        if page_data:
            for point in page_data:
                if point['uuid'] not in self.scraped_points:
                    yield Request(
                        CHARGE_POINT_DETAILS_ENDPOINT.format(uuid=point['uuid']),
                        headers=self.auth_headers,
                        callback=self.parse_charge_point_details,
                        cb_kwargs={'date_created': point['created_at']}
                    )

            if current_page < last_page:
                yield Request(
                    BOUNDING_BOX_FILTER_URL.format(latitude=latitude, longitude=longitude, page=current_page+1),
                    headers=self.auth_headers,
                    callback=self.low_level_boundary_search,
                    cb_kwargs={'latitude': latitude, 'longitude': longitude},
                    dont_filter=True
                )

    def parse_charge_point_details(self, response: Response, date_created: str):
        details = json.loads(response.text)['data']
        if details['country'].upper() == 'GB':
            city = details['city'] or ''
            state = details['state'] or ''
            street_address = details['address'] or ''
            postal_code = details['postal_code'] or ''
            address = " ".join([field for field in [street_address, city, state, postal_code] if field])
            parking_fee = details['parking'].get('fee') or ''
            charging_fee = ''
            devices = details['devices']
            if len(devices) > 0:
                charging_fee = devices[0]['payment_details']['pricing']
            operator_name = details['operator']['name'] or ''
            phone_number = details['owner']['telephone_number'] or ''

            formatted_detail = {
                'uuid': details['uuid'],
                'name': details['name'],
                'city': city,
                'state': state,
                'street_address': street_address,
                'postal_code': postal_code,
                'full_address': address,
                'phone_number': phone_number,
                'date_created': parse_date(date_created),
                'date_updated': parse_date(details['updated_at']),
                'parking_fee': parking_fee,
                'charging_fee': charging_fee,
                'operator_name': operator_name,
                'location_url': f"https://www.zap-map.com/charge-points/helston/{details['uuid']}/"
            }
            yield formatted_detail
