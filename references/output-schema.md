# PaedsEngage parser output schema

The bundled parser writes four table-oriented outputs.

## clinics.json
Array of clinic objects:
- `location`: PDF location/area heading.
- `clinic_name`: parsed clinic name.
- `doctors`: list of doctors.
- `address`: clinic address.
- `contacts`: list of 8-digit phone numbers.
- `contact_primary`: first parsed phone number.
- `contact_notes`: non-phone contact notes.
- `google_maps_url`: Google Maps search URL generated from clinic name + address.
- `operating_hours_text`: original normalized hours lines.
- `schedule.days`: parsed day/time blocks for filtering.
- `schedule.general_notes`: hours notes that could not be assigned to a day.

## clinics.csv
One row per clinic. Doctors, contacts, hours, and notes are pipe-delimited.

## clinic_hours.csv
One row per clinic/day with aggregated time blocks and notes.

## clinic_hours_blocks.csv
One row per clinic/day/time block with normalized `start`, `end`, minute offsets, overnight flag, and display string.

## Known limitations
- PDF column extraction is layout-sensitive; spot-check names, addresses, and hours after each new source PDF.
- Google Maps coordinates/status are not included by this parser. Use a separate geocoding/Places audit step when needed.
- Clinics with split names or unusual hours may require manual review.
