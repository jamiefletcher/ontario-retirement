# Ontario Retirement

An up-to-date dataset of privately-run retirement homes in Ontario, Canada. These facilities are regulated by the [Retirement Homes Regulatory Authority](https://www.rhra.ca/) (RHRA) which continuously updates its register of licenses, inspections and enforcement actions.

## Why Collect these Data?

The health system in Ontario is under pressure and publicly-run [long-term care homes](https://www.ontario.ca/page/long-term-care-ontario) have long waiting lists to accept new residents. Older Ontarians who need care must therefore look to privately-run retirement homes but these homes vary considerably in the level of services that they offer. Finding a good home, with the right services, and convenient location is an urgent problem.

## Using the Dataset

We provide the dataset in two formats: 
- `rhra_resister.json` provides a full list of all retirement homes in Ontario. This includes facilities that have closed or had their licenses terminated for various reasons.
- `homes.geojson` provides a list shorter list of those retirement homes in Ontario that are currently operating. This dataset can be visualized using our simple web interface, which includes the ability to search and filter the facilities.

### Services

The dataset tracks 13 categories of services that are offered by private retirement homes. While many of these services are commonly offered (e.g. provision of meals, assistance with personal hygiene), other services are offered by relatively few homes (e.g. dementia care, skin and wound care).

- Assistance with bathing
- Assistance with personal hygiene
- Assistance with ambulation
- Assistance with feeding
- Provision of skin and wound care
- Continence care
- Administration of drugs or another substance
- Provision of a meal
- Dementia care program
- Assistance with dressing
- Any service that a member of the Ontario College of Pharmacists provides while engaging in the practice of pharmacy
- Any service that a member of the College of Physicians and Surgeons of Ontario provides while engaging in the practice of medicine
- Any service that a member of the College of Nurses of Ontario provides while engaging in the practice of nursing

### Enforcement

When selecting retirement home, it is useful to be aware of the regulatory status of any homes under consideration. Various regulatory enforcement actions may be taken to ensure safety of retirement home residents.

- **License status**: `Issued` vs `Issued with conditions`. Conditions placed directly on a facility's license may require the home to carry out specific mandatory actions to ensure proper care for the residents.
- **Orders**. Even if conditions are not imposed on the license, a facility may be ordered to carry out specific mandatory actions to ensure proper care for the residents.
- **Inspection type**: `Report` vs `Mandatory Report`. The RHRA completes regular inspections of facilities on a three-year interval. However, if complaints are received about a home, a mandatory inspection will be completed.