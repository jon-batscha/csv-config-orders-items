# csv-config-orders-items

This package is a clone of the [config-driven-csv package](https://github.com/jon-batscha/config-csv-ingestion), with one important distinction:

The linked package generalizes for any event type, but only works for flat (non-nested data).

For that reason, we created this package to merge ordered-items into placed-order events.

NOTE: This README is very brief, as most of the functionality/limitations are inherited from the linked package; we only cover the differences.

## Key Difference

Input Data: This package assumes csv file is a single ordered_items file that contains in each row enough data to generate both PlacedOrder and OrderedItem events. The example data will be instructive.

This package has a newly-written csv_to_orders function that, given a few inputs, converts a csv into a list of ORDER payloads. Any other events that are generated (items, etc) should use the general csv_to_payload in this package

Because of that, there is a unique config format for Order events for this script to generalize: Instead of a single `properties` key, there are 3 different keys for mapping properties:
- `properties`: for mapping properties that can be inferred from a single ordered_item row (e.g. OrderType)
- `summed_properties`: for properties that should be summed across all ordered_items in a given order (e.g: Price)
- `listed_properties`: for properties that should be listed for a given Order (e.g. ItemNames, Size, etc)

NOTE: There are a few other minor differences between this package and the linked package, in terms of how similarly named functions are implemented (due to this package being a temprary branch off the linked package). For that reason, I recommend that any script uses only one or the other package (though you can have separate scripts each running a different package pushing to the same account). This package will be merged into the linked one soon, but I prioritized getting an MVP out asap.

