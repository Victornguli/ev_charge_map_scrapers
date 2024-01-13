from pathlib import Path

import requests
from geopy import Nominatim
from scrapy.exceptions import DropItem

from charge_point_scrapers.constants import XLSX_OUT_FILE, SheetNames
from charge_point_scrapers.utils import export_to_excel, fmt_co_charger_value


class ZapMapsPipeline:

    def __init__(self, crawler):
        self.crawler = crawler
        self.seen_uids = set()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        if item['uuid'] not in self.seen_uids:
            self.seen_uids.add(item['uuid'])
        else:
            raise DropItem(f"Duplicate item dropped {item}")

        return item


class ZapMapsOutPipeline:

    def close_spider(self, spider):
        root_dir = Path(__file__).parent.parent
        feeds = spider.settings.get('FEEDS')
        feed_paths = list(feeds.keys())
        jsonl_feed_path = None
        if feed_paths and feeds[feed_paths[0]]['format'] == 'jl':
            jsonl_feed_path = root_dir / feed_paths[0]

        if not jsonl_feed_path or not jsonl_feed_path.exists():
            spider.logger.error("Failed to export. JL Feed export not found")
            return

        excel_file_path = root_dir / XLSX_OUT_FILE
        sheet_name = SheetNames.ZAP_MAP.value
        col_mapping = {
            'name': 'Name',
            'full_address': 'Full Address',
            'street_address': 'Street Address',
            'city': 'City',
            'state': 'County',
            'postal_code': 'Post Code',
            'phone_number': 'Phone Number',
            'operator_name': 'Charge Point Operator Name',
            'date_created': 'Date Created',
            'date_updated': 'Date Updated',
            'charging_fee': 'Charging fee',
            'parking_fee': 'Parking fee',
            'location_url': 'Location URL'
        }

        export_to_excel(
            excel_file_path=excel_file_path,
            jsonl_feed_path=jsonl_feed_path,
            col_mapping=col_mapping,
            sheet_name=sheet_name,
            spider=spider
        )


class CoChargerRawPipeline:
    def __init__(self, crawler):
        self.crawler = crawler
        self.seen_ids = set()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        if item['id'] not in self.seen_ids:
            self.seen_ids.add(item['id'])
        else:
            raise DropItem(f"Duplicate item dropped {item}")

        if not item['status']:
            raise DropItem(f"Invalid host dropped {item}")

        geolocator = Nominatim(user_agent='some random ua')
        invalid_values = ['', 'null', None]
        if item['city'] in invalid_values:
            loc = geolocator.geocode(item['post_code'], addressdetails=True).raw
            addr = loc['address']
            city = addr.get('city') or \
                addr.get('town') or \
                addr.get('village') or \
                addr.get('city_district') or \
                addr.get('suburb') or \
                addr.get('county')
            if city:
                item['city'] = city

        if item['county'] in invalid_values:
            res = requests.get(f"https://wikishire.co.uk/lookup/postcode?pc={item['post_code']}")
            county = res.text
            if county:
                item['county'] = county

        first_name, last_name = fmt_co_charger_value(item['first_name']), fmt_co_charger_value(item['last_name'])
        name = f"{first_name} {last_name}".strip()

        address_line_1, address_line_2 = fmt_co_charger_value(item['address_line_1']), fmt_co_charger_value(item['address_line_2'])
        address = f"{address_line_1} {address_line_2}".strip()

        item.update(name=name, address=address)

        return item


class CoChargerOutPipeline:

    def close_spider(self, spider):
        root_dir = Path(__file__).parent.parent
        feeds = spider.settings.get('FEEDS')
        feed_paths = list(feeds.keys())
        jsonl_feed_path = None
        if feed_paths and feeds[feed_paths[0]]['format'] == 'jl':
            jsonl_feed_path = root_dir / feed_paths[0]

        if not jsonl_feed_path or not jsonl_feed_path.exists():
            spider.logger.error("Failed to export. JL Feed export not found")
            return

        excel_file_path = root_dir / XLSX_OUT_FILE
        sheet_name = SheetNames.CO_CHARGER.value
        col_mapping = {
            'name': 'Name of the Host',
            'address': 'Street Address',
            'city': 'City',
            'county': 'County',
            'post_code': 'Post Code',
            'mobile': 'Phone Number',
            'charging_rate': 'Charging rate (kW)',
            'charger_type': 'Connector type',
            'charge_cost_rate': 'Rental charge (£/hour)',
        }
        export_to_excel(
            excel_file_path=excel_file_path,
            jsonl_feed_path=jsonl_feed_path,
            col_mapping=col_mapping,
            sheet_name=sheet_name,
            spider=spider
        )
