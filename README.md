# Plant by Frost

A garden planting calendar for the U.S. Enter a ZIP code and it shows what to plant and when, for 95 vegetables, herbs, fruits and nuts, timed from the average frost dates where you live.

## What it does

- **Frost dates for your ZIP code** from the nearest NOAA weather station, with the median date and the 1-in-10-years early or late date.
- **USDA hardiness zone** for your ZIP code (2023 map). Fruit trees and perennials outside your zone are flagged.
- **This week:** what to start indoors, what to plant outside, and what's coming up in the next three weeks.
- **Year calendar:** start-indoors, spring and fall planting windows for every plant, with spacing, depth, days to harvest and growing tips.
- **Your own frost dates:** if your spot runs early or late, set your own dates and the whole calendar moves.
- **My garden:** star plants to keep a short list.

Every planting window is counted in weeks from your last spring frost or first fall frost, so the same plant list works anywhere. Warm-season crops that can be sown again and again (beans, corn, squash) keep their window open until there's just enough time left to harvest before the first fall frost.

## Data sources

- Frost dates: NOAA National Centers for Environmental Information, U.S. Climate Normals 1991–2020 (annual/seasonal, by station), 32°F frost probabilities.
- Hardiness zones: 2023 USDA Plant Hardiness Zone Map by ZIP code, USDA Agricultural Research Service and the PRISM Climate Group, Oregon State University.
- ZIP code places and coordinates: GeoNames, CC BY 4.0.

Planting windows are general guides built from common extension-service timing. Your county extension office has the final word for your area.

## Building

The page is a single `index.html` with the frost and ZIP data built in (no server, no API calls).

1. Download the source data into `tools/`:
   - NOAA normals archive: `us-climate-normals_1991-2020_v1.0.1_annualseasonal_multivariate_by-station_c20230404.tar.gz` from <https://www.ncei.noaa.gov/data/normals-annualseasonal/1991-2020/archive/>, extracted
   - `phzm_us_zipcode_2023.csv` (plus `ak`, `hi`, `pr`) from <https://prism.oregonstate.edu/phzm/>, saved as `zone_us.csv` and so on
   - `US.zip` from <https://download.geonames.org/export/zip/>, extracted to `geonames/US.txt`
2. `python tools/build_data.py` writes `frostdata.js`.
3. `python tools/build_site.py index.html` writes the page from `template.html`.
