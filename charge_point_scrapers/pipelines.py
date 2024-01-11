from pathlib import Path

from scrapy.exceptions import DropItem
from charge_point_scrapers.utils import export_to_excel


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

        excel_file_path = root_dir / 'EvPointsZapmapCocharger.xlsx'
        sheet_name = 'Zap Map'
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
