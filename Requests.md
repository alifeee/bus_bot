# Requests

More information about specific requests.

## Eligible journeys

These get all stops etc, so bot user can select the stops they use, to filter results to only those stops.

```yaml
data: list (of days)
  ...
  id: string (day id)
  name: string
  journeys: list (of journeys)
    id: string
    start_date: string
    end_date:
    journey:
      ...
      journey_type: OUTBOUND | RETURN
      route_id: string (not used)
      id: string (used in journeys)
      origin_pickup_id: string (first stop)
      origin_pickup_name: string
      destination_pickup_id: string (last stop)
      destination_pickup_name: string
      journey_stops: list
        ...
        journey_id: string (id of parent journey)
        id: string
        name: string
        journey_stop_id: string (journey-specific stop id, used in capacity)
        arrival_datetime: string
        departure_datetime: string
        location:
          location_id: string
          stop_id: string
```

## Stops

All stop information is retrievable from eligible journeys. We do not need to duplicate API requests.

## Journeys

These are specific to the pickup/dropoff points. Bot user should be able to select some of these to track.

Bot user picks journeys to track at the start of each week (perhaps annoying, but guarantees that journeys exist)

```yaml
data: list of journeys
  ...
  type: OUTBOUND | RETURN
  departure_date: string
  arrival_date: string
  journey_id: string
  origin:
    id: string (per journey)
    stop_id: string (constant for stop)
  destination:
    id: string
    stop_id: string
```

## Capacity

This links the `journey_id` from Journeys to a capacity. Usually it is 0 if the book is booked out.

We would notify the bot user if the capacity becomes greater than after being 0.

```yaml
string: int
```
