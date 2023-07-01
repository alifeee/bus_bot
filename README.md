# Bus bot

Telegram bot to notify when seats are available on a bus.

## Requests

List of requests for the information we need

| API | Description | Used by | URL | Query Parameters? | Notes |
| --- | --- | --- | --- | --- | --- |
| eligible_journeys | Get journeys for pass ID | [Rides page] | <https://app.zeelo.co/api/travels/38u1fj13-rfd8-q99a-ap22-ao92929ifikf/elegible-journey-groups>|❌||
| stops | Get stops | [Rides page] | <https://app.zeelo.co/api/stops/by_id?page=1&per_page=25>|❌||
| journeys | Get journeys | [Pass page] | <https://app.zeelo.co/api/travel-passes/38u1fj13-rfd8-q99a-ap22-ao92929ifikf/eligible-journey-groups>|✅||
| capacity | Get capacity | [Pass page] | <https://app.zeelo.co/api/journeys/capacity_between_stops>|❌||

[Rides page]: https://app.zeelo.co/rides/jlr
[Pass page]: https://app.zeelo.co/my-zeelo/travel-pass/38u1fj13-rfd8-q99a-ap22-ao92929ifikf

## Journeys URL parameters

| Parameter | Description | Example |
| --- | --- | --- |
| product_id | Product ID | 38u1fj13-rfd8-q99a-ap22-ao92929ifikf |
| origin_stop_id[] | Origin stop ID | 38u1fj13-rfd8-q99a-ap22-ao92929ifikf |
| destination_stop_id[] | Destination stop ID | 38u1fj13-rfd8-q99a-ap22-ao92929ifikf |
| tier_id[] | Tier ID | 38u1fj13-rfd8-q99a-ap22-ao92929ifikf |

### Example URL

<https://app.zeelo.co/api/travel-passes/38u1fj13-rfd8-q99a-ap22-ao92929ifikf/eligible-journey-groups?product_id=38u1fj13-rfd8-q99a-ap22-ao92929ifikf&origin_stop_id[]=38u1fj13-rfd8-q99a-ap22-ao92929ifikf&destination_stop_id[]=38u1fj13-rfd8-q99a-ap22-ao92929ifikf&tier_id[]=38u1fj13-rfd8-q99a-ap22-ao92929ifikf>
