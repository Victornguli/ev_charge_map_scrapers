## Ev Charging point scrapers for ZapMap and Co Charger maps
Scrapes [Co Charger](https://co-charger.com/map/) and [Zap Map](https://www.zap-map.com/live/) to extract EV charging points in UK territory

### Requirements

1. The scrapers are built using [scrapy](https://scrapy.org/) framework and requires **[Python3.8+](https://www.python.org/downloads/)**
2. A free Co charger account with your address set to a central region in the UK. Your profile address is crucial since co charger filters from your location's radius 

### Getting started

Follow the following instructions to get started 
- Ensure Python3.8+ is installed by running `python3 --version` in your terminal/command line
- Clone this repo by running `git clone https://github.com/Victornguli/ev_charge_map_scrapers.git`
- run `cd ev_charge_map_scrapers` to navigate into the cloned repo
- Create and activate a virtualenv using your preferred method. 
  - To use **[virtualenv](https://pypi.org/project/virtualenv/)** run 
      ```
       python3 -m pip install virtualenv &&\
       python3 -m virtualenv venv &&\
       source venv/bin/activate
      ```
- Run `pip install -r requirements.txt` to install the requirements
- Run `cp sample.env .env`
- Inside **.env** follow this guide to set the needed configuration
  
  | Name| Description                                                                                                | Notes                                                                                                                                                                                              |
  ------|------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | CO_CHARGER_EMAIL | Your Co Charger account email                                                                              | Required to scrape Co Charger                                                                                                                                                                      |
  | CO_CHARGER_PASSWORD | Your Co Charger account password                                                                           | Required to scrape Co Charger                                                                                                                                                                      |
  | CO_CHARGER_IGNORE_20_MILE_RADIUS | Control flag to dictate whether to scrape all of UK co charger hosts or use preset location radius filters | Accepts 0 or 1 and defaults to 0                                                                                   |
  | CO_CHARGER_TOKEN | The Co charger mobile auth token.| Do not set this, leave the value empty on the first run.|


### Running the scrapers
#### Zap Maps
To scrape Zap Map, run 
 ```
 scrapy crawl zap_maps -o zap_maps.jl
 ```


#### Co Charger
Ensure you have set the correct email and password in the .env file as described in the getting started step and run:
```
scrapy crawl co_charger -o co_charger.jl
```

Once the scrapers are done, an Excel file output will be generated in the same folder.

### Other details
The scrapers will save intermediate data as **[jsonlines](https://jsonlines.org/)**. Do not clear, tamper or delete these unless you want a full re-scrape of the targets.

On subsequent runs, only new hosts or charging points will be scraped.


#### Co-Charger specific
These details only apply to the co_charger scraper.
1. AVOID tampering with **CO_CHARGER_TOKEN**.
2. After the first successful login attempt **CO_CHARGER_TOKEN** will be updated in the .env for future scrapes.
3. If you get 401 errors clear the value so that the entry becomes
`CO_CHARGER_TOKEN=` and simply re-run the co_charger scraper
4. `CO_CHARGER_IGNORE_20_MILE_RADIUS` defaults to 0 and will return hosts within a 20 mile radius of each preset location.
5. If `CO_CHARGER_IGNORE_20_MILE_RADIUS` is set to 1 the scraper will return all active hosts in UK, effectively 
ignoring the 20 mile radius filters of the preset locations.
6. These are the preset locations used. 
   - Peterborough 
   - Oxfordshire 
   - Wimbledon
   - Bristol 
   - Birmingham 
   - Manchester 
   - Milton Keynes 
   - Reading
