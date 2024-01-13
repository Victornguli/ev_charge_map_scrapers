import json
import os
from pathlib import Path

import requests
import scrapy
from dotenv import load_dotenv
from scrapy import Request
from geopy.geocoders import Nominatim

from charge_point_scrapers.constants import CO_CHARGER_REQUEST_HEADERS, EnvKeys
from charge_point_scrapers.utils import authenticate_co_charger, update_co_charger_auth_token


class CoChargerSpider(scrapy.Spider):
    name = "co_charger"
    # handle_httpstatus_list = [401, 403]
    allowed_domains = ['api.co-charger.com']
    custom_settings = {
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 429],
        'RETRY_TIMES': 3,
        'ITEM_PIPELINES': {
            'charge_point_scrapers.pipelines.CoChargerRawPipeline': 100,
            'charge_point_scrapers.pipelines.CoChargerOutPipeline': 99999,
        }
    }
    auth_headers = {}

    def get_charging_hosts(self, auth_token: str, limit: int = 1000):
        return Request(
            f'https://api.co-charger.com/hostsearch/{limit}/{auth_token}/1',
            headers=CO_CHARGER_REQUEST_HEADERS,
            callback=self.parse_hosts
        )

    def start_requests(self):
        self.scraped_hosts = {}
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
                    self.scraped_hosts[line_data['id']] = 1

        self.logger.info(f"Loaded {len(self.scraped_hosts.keys())} scraped points")

        load_dotenv()
        co_charger_token = os.getenv(EnvKeys.CO_CHARGER_TOKEN.value)
        if co_charger_token:
            yield self.get_charging_hosts(co_charger_token)
        else:
            yield authenticate_co_charger(callback=self.parse_login)

    def parse_login(self, response):
        parsed_res = json.loads(response.text)
        if 'token' in parsed_res:
            auth_token = parsed_res['token']
            update_co_charger_auth_token(auth_token)
            yield self.get_charging_hosts(auth_token)

    def parse_hosts(self, response):
        parsed_res = json.loads(response.text)
        for host in parsed_res['hosts']:
            if host['id'] not in self.scraped_hosts:
                yield host
