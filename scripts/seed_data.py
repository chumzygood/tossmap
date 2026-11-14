"""Seed data: every entry verified against the cited official source on its `checked` date."""
import json
HHW="Household hazardous waste (paint, chemicals, pesticides, automotive fluids, batteries, bulbs)"
def F(name,address,hours,source,accepts=HHW,fees="",notes="",checked="2026-11-02"):
    return dict(name=name,address=address,hours=hours,accepts=accepts,fees=fees,notes=notes,source=source,checked=checked)
M=[]
def metro(city,state,st,facs,note=""):
    M.append(dict(city=city,state=state,st=st,facilities=facs,note=note))
NYC="https://www.nyc.gov/site/dsny/what-we-do/programs/special-waste-drop-off.page"
nyacc="Aerosols, batteries, e-waste, vapes, fluorescent bulbs/CFLs, motor oil (10 qt), oil filters (2), paint (5 gal), passenger tires (4), mercury devices (2)"
metro("New York","New York","NY",[F(f"DSNY Special Waste Drop-Off – {b}",a,"Tue–Sat 9am–3pm",NYC,nyacc,"Free","NYC residents only; proof of residency required") for b,a in [("Bronx","Farragut St & East River, Hunts Point, Bronx, NY"),("Brooklyn","459 North Henry St, Greenpoint, Brooklyn, NY"),("Manhattan","74 Pike Slip, New York, NY"),("Queens","30th Ave between 120th & 122nd St, College Point, Queens, NY"),("Staten Island","Fresh Kills, off Muldoon Ave exit of West Shore Expwy, Staten Island, NY")]])
LA="https://sanitation.lacity.gov/programs/safe-centers-and-household-hazardous-waste"
laacc="Motor oil & filters, paint & solvents, e-waste, cleaners, batteries, fluorescent bulbs, sharps, unused medicine (no tires)"
metro("Los Angeles","California","CA",[F(n,a,"Sat–Sun 9am–3pm",LA,laacc,"Free") for n,a in [("S.A.F.E. Center – Nicole Bernson","10241 N Balboa Blvd, Northridge, CA 91325"),("S.A.F.E. Center – Gaffey St","1400 N Gaffey St, San Pedro, CA 90731"),("S.A.F.E. Center – Hyperion","7660 W Imperial Hwy, Gate B, Playa del Rey, CA 90293"),("S.A.F.E. Center – Randall St","11025 Randall St, Sun Valley, CA 91352"),("S.A.F.E. Center – Washington Blvd","2649 E Washington Blvd, Los Angeles, CA 90021")]]+[F("UCLA S.A.F.E. Collection Center","550 Charles E Young Dr, Los Angeles, CA","Fri, Sat & first Sun 9am–3pm","https://ehs.ucla.edu/safe-collection-center-operations-ucla",laacc,"Free")],"LA-Glendale S.A.F.E. Center (4600 Colorado Blvd) is listed by the city as temporarily closed.")
metro("Chicago","Illinois","IL",[F("Household Chemicals & Computer Recycling Facility","1150 N North Branch St, Chicago, IL 60642","Tue 7am–12pm; Thu 2–7pm; 1st Sat 8am–3pm","https://www.chicago.gov/hccrf/","Chemicals, oil-based paint, solvents, CFLs, computers & electronics, cell phones (no latex paint)","Free")])
H="https://houstontx.gov/solidwaste/esc.html"
metro("Houston","Texas","TX",[F("Environmental Service Center – South","11500 S Post Oak Rd, Houston, TX 77035","Tue, Wed, Fri, Sat 8am–5pm",H,notes="Texas ID or City utility bill required"),F("Environmental Service Center – North","5614 Neches St, Houston, TX 77026","2nd Thursday 9am–3pm",H,notes="Texas ID or City utility bill required")]+[F(f"Residential Drop-Off Center – {n}",a,"Tue–Sat 9am–6pm","https://houstontx.gov/solidwaste/depository.html","Passenger tires (5 per visit, 10 per month), used motor oil (5 qt), aerosol cans, bulk items, appliances, mattresses, recyclables (no paint, chemicals, TVs or truck tires)","Free","Houston residents; Texas ID or City utility bill/lease; up to 4 visits per month",checked="2026-11-03") for n,a in [("North","9003 N Main, Houston, TX 77022"),("Northwest","14400 Sommermeyer, Houston, TX 77041"),("Northeast","5565 Kirkpatrick, Houston, TX 77028"),("Southeast","2240 Central Street, Houston, TX 77017"),("South","5100 Sunbeam, Houston, TX 77033"),("Southwest","10785 SW Freeway, Houston, TX 77074")]])
PHX="https://www.phoenix.gov/administration/departments/publicworks/about-us/transfer-stations.html"
phxacc="Passenger car tires (5 per year, rims removed; no off-road, semi or motorcycle tires), appliances, CRT and non-CRT TVs (2 CRTs/month free), household trash"
metro("Phoenix","Arizona","AZ",[F(n,a,"Mon–Fri 5:30am–5pm; Sat 6am–3pm; closed Sun & city holidays (closed Wed Nov 11, 2026)",PHX,phxacc,"Residents: one load up to 1 ton/month free with city services bill + matching photo ID; otherwise $55/ton ($40 min); extra CRTs $20 each","Household hazardous waste is prohibited",checked="2026-11-04") for n,a in [("North Gateway Transfer Station","30205 N. Black Canyon Hwy., Phoenix, AZ 85085"),("27th Avenue Transfer Station","3060 S. 27th Ave., Phoenix, AZ 85009")]],"Phoenix has no public HHW drop-off; residential customers get one at-home HHW collection per year. The 27th Ave Transfer Station does not accept HHW. Source: https://www.phoenix.gov/administration/departments/publicworks/residential-trash-recycling/household-hazardous-waste-collection.html")
metro("Philadelphia","Pennsylvania","PA",[],"Philadelphia HHW is event-only. The last 2026 event was Sat Nov 7, 2026 (Port Richmond, 3901 N Delaware Ave); no remaining 2026 dates. Watch the city page for 2027 dates. Electronics are not accepted at HHW events — take them to a Sanitation Convenience Center. Source: https://www.phila.gov/services/trash-recycling-city-upkeep/dispose-of-household-hazardous-waste/")
SAB="https://www.sa.gov/Directory/Departments/SWMD/Brush-Bulky/Bulky-Drop-Off"
metro("San Antonio","Texas","TX",[F("Household Hazardous Waste Drop-Off Center","7030 Culebra Rd, San Antonio, TX 78238","Tue–Fri 8am–5pm; Sat 8am–noon","https://www.sa.gov/Directory/Departments/SWMD/HHW",notes="Bring CPS Energy bill showing Environmental Fee + photo ID")]+[F(f"Bulky Waste Collection Center – {n}",a,"Tue–Fri 8am–5pm; Sat 8am–4pm",SAB,"Car tires (6 or fewer, no rims), large appliances, furniture, mattresses, carpeting, auto parts, water heaters & AC units, construction material (1 cu yd or less)","Free with City environmental fee","Residential customers only; bring a recent CPS Energy bill + photo ID; no household trash or hazardous material",checked="2026-11-05") for n,a in [("Bitters","1800 Wurzbach Parkway, San Antonio, TX 78216"),("Frio City Road","1531 Frio City Road, San Antonio, TX 78226"),("Culebra","7030 Culebra Road, San Antonio, TX 78238"),("Rigsby Road","2755 Rigsby Road, San Antonio, TX 78222")]],"Next Free Landfill Day: Sat Nov 14, 2026, 8am–1pm at Republic Services Landfill (7000 IH 10 E) and Waste Management Landfill (8611 Covel Rd); tires limit 6 passenger car tires per household (re-verified 2026-11-09). Source: https://www.sa.gov/Directory/Departments/SWMD/Garbage/Landfill")
metro("San Diego","California","CA",[F("HHW Transfer Facility (Miramar Landfill)","5161 Convoy St, San Diego, CA 92111","Wed & Sat 9am–3pm, by appointment","https://www.sandiego.gov/environmental-services/ep/hazardous",fees="Free for City residents",notes="Appointment required")])
metro("Dallas","Texas","TX",[F("Dallas County Home Chemical Collection Center","11234 Plano Rd, Dallas, TX 75243","Tue 9am–7:30pm; Wed–Thu 8:30am–5pm; 2nd & 4th Sat 9am–3pm","http://www.dallascounty.org/departments/consolidated-services/hhw/",notes="Residents of participating cities; 214-553-1765")])
metro("Austin","Texas","TX",[F("Recycle & Reuse Drop-off Center","2514 Business Center Dr, Austin, TX 78744","By appointment (hours not published)","https://www.austintexas.gov/resource-recovery/locations/recycle-and-reuse-drop-center",notes="Appointment required")])
metro("Jacksonville","Florida","FL",[F("Household Hazardous Waste Facility","2675 Commonwealth Ave, Jacksonville, FL 32254","Tue–Sat 8am–5pm","https://www.jacksonville.gov/departments/office-of-administrative-services/solid-waste/disposal-operations/household-hazardous-wastes-(hhw)","Paint, motor oil, batteries, fluorescent/CFL bulbs, aerosols, fertilizers, photo chemicals, drain cleaners, fuels, fireworks, household e-waste",notes="Paint/oil limit 27 gal each per 30 days; CRT TVs/monitors max 3; 904-387-8847")])
FWD="https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/dropoff"
metro("Fort Worth","Texas","TX",[F("Environmental Collection Center","6400 Bridge St, Fort Worth, TX 76112","Thu–Fri 11am–7pm; Sat 9am–3pm","https://www.fortworthtexas.gov/departments/environmental-services/solidwaste/environmental-collection-center/environmental-collection-center","Automotive fluids, batteries, cleaners/chemicals, paint, lawn & pool chemicals, bulbs, cooking oil")]+[F(f"{n} Drop-Off Station",a,"Tue–Fri 8am–5pm; Sat 8am–noon; closed Sun–Mon and city holidays (incl. Thanksgiving and the day after)",FWD,"Passenger tires (4 per household every 6 months, rims separated), computers & TVs (2 every 6 months), household chemicals incl. paint and motor oil (20 gal every 3 months), all batteries, light bulbs, appliances, bulky trash, recycling","Free for residents","Fort Worth residents with a City solid waste account: bring a water bill (within 6 months) + matching driver's license; apartment residents may bring recycling and HHW with a driver's license",checked="2026-11-05") for n,a in [("Brennan","2400 Brennan Ave, Fort Worth, TX"),("Southeast","5150 Martin Luther King Fwy, Fort Worth, TX"),("Old Hemphill Road","6260 Old Hemphill Rd, Fort Worth, TX"),("Hillshire (North Service Center)","301 Hillshire Dr, Fort Worth, TX")]])
metro("Columbus","Ohio","OH",[F("SWACO Household Hazardous Waste Drop-Off","645 E 8th Ave, Columbus, OH 43201","Mon–Fri 9am–5pm; 1st Sat 9am–2pm","https://www.swaco.org/diversion/residents/household-hazardous-waste/",notes="614-294-1300; closed holidays")])
MK="https://wipeoutwaste.mecknc.gov/where-can-i-recycle"
metro("Charlotte","North Carolina","NC",[F(n,a,"Mon–Sat 7am–4pm",MK,notes="Mecklenburg residents; no business HHW; tell staff you have hazardous materials") for n,a in [("Compost Central Disposal & Recycling Center","140 Valleydale Rd, Charlotte, NC 28214"),("Foxhole Disposal & Recycling Center","17131 Lancaster Hwy, Charlotte, NC 28277"),("Hickory Grove Disposal & Recycling Center","8007 Pence Rd, Charlotte, NC 28215"),("North Mecklenburg Disposal & Recycling Center","12300 Statesville Rd, Huntersville, NC 28078")]])
KC="https://kingcounty.gov/en/dept/dnrp/waste-services/hazardous-waste-program/household/disposal-facilities"
metro("Seattle","Washington","WA",[F("North Seattle HHW Facility","12550 Stone Ave N, Seattle, WA 98133","Sun–Tue 9am–5pm",KC,fees="Free",notes="King County residents; no appointment"),F("South Seattle HHW Facility","8100 2nd Ave S, Seattle, WA 98108","Thu–Sat 9am–5pm",KC,fees="Free",notes="King County residents; no appointment")])
metro("Denver","Colorado","CO",[F("Rooney Road Recycling Center","151 S Rooney Rd, Golden, CO 80401","Wed & Sat 8am–2pm, by appointment","https://www.rooneyroadrecycling.org/",notes="Appointment required")],"Denver's own program is at-your-door pickup ($15, once per year; 1-800-449-7587). Source: https://denvergov.org/My-Property/Recycle-Compost-Trash/Recycle/Household-Hazardous-Waste/Household-Hazardous-Waste-At-Your-Door-Collection")
IN="https://www.indy.gov/activity/hazardous-waste-dropoff-sites"
metro("Indianapolis","Indiana","IN",[F("ToxDrop – Traders Point Collection Facility","7550 N Lafayette Rd, Indianapolis, IN","1st Sat 9am–2pm",IN,HHW+"; electronics","Free for Marion County residents"),F("ToxDrop – Perry Township Government Center","4925 S Shelby St, Indianapolis, IN","2nd & 4th Sat 9am–2pm",IN,HHW+"; electronics","Free for Marion County residents")])
metro("San Francisco","California","CA",[F("Recology SF Household Hazardous Waste Facility","501 Tunnel Ave, San Francisco, CA","Thu–Sat 8am–4pm","https://www.recology.com/recology-san-francisco/hazardous-waste/",notes="SF residents only; proof of residency")])
PM="https://www.oregonmetro.gov/waste-disposal-and-prevention/need-get-rid-something/household-hazardous-waste"
metro("Portland","Oregon","OR",[F("Metro Central Hazardous Waste","6161 NW 61st Ave, Portland, OR 97210","Mon–Sat 9am–4pm",PM,fees="Free for households (up to 35 gal/visit)"),F("Metro South Hazardous Waste","2001 Washington St, Oregon City, OR 97045","Daily 9am–4pm",PM,fees="Free for households (up to 35 gal/visit)")])
NS="https://www.nashville.gov/departments/waste-services/convenience-centers/household-hazardous-waste"
metro("Nashville","Tennessee","TN",[F(n,a,"Tue–Sat 8:30am–4:30pm",NS,fees="Free",notes="Davidson County residents; TN driver's license; 15 gal or 100 lb/month") for n,a in [("East Convenience Center","943A Doctor Richard G. Adams Dr, Nashville, TN 37207"),("Ezell Pike Convenience Center","3254 Ezell Pike, Nashville, TN 37211")]])
metro("Washington","District of Columbia","DC",[F("Fort Totten Transfer Station (tires)","4900 John McCormack Rd NE, Washington, DC 20011","Tue–Fri 10am–2pm; Sat 7am–2pm; closed Mon & District holidays","https://dpw.dc.gov/service/household-hazardous-waste-hhw-e-cycling-document-shredding",accepts="Passenger tires (up to 4); bulk trash, recycling, yard waste and appliances during regular hours",fees="Free for DC residents",notes="DC residents only; proof of residency required. HHW and electronics are NOT accepted here — use Special Waste Collection Events.",checked="2026-11-09"),F("DPW Special Waste Collection Event – RFK Stadium Lot 8","2500 Independence Ave SE, Washington, DC 20003","Event: Sat Nov 14, 2026, 8am–2pm (registration required; no entry after 2pm)","https://dpw.dc.gov/service/household-hazardous-waste-hhw-e-cycling-document-shredding",accepts="HHW (paints, chemicals, batteries, CFLs, motor oil, auto fluids, propane ≤20 lb); e-waste (computers, TVs, phones, printers, monitors); document shredding (up to 5 boxes)",fees="Free",notes="DC residents only; register in advance on Eventbrite; bring proof of residency and registration. Next listed event after this: Sat Dec 12, 2026, also at RFK Lot 8.",checked="2026-11-09")],"No permanent HHW or e-cycling drop-off. Fort Totten takes up to 4 tires during regular hours. HHW and electronics are collected at registered DPW Special Waste Collection Events. Source: https://dpw.dc.gov/service/household-hazardous-waste-hhw-e-cycling-document-shredding")
metro("Boston","Massachusetts","MA",[F("Zero Waste Day Drop-Off – Millennium Park","315 Gardner St, West Roxbury, MA 02132","Event: Sat Nov 21, 2026, 8:30am–noon","https://www.boston.gov/departments/public-works/zero-waste-day","Hazardous chemicals (20 gal limit), oil-based paint, rechargeable/lithium batteries, electronics (computers, phones, TVs, printers), fluorescent bulbs/mercury items, car & bike tires (8 each), car batteries, propane tanks, fire extinguishers","Free","Boston residents only; photo ID, utility bill or lease. Rescheduled from Sept 26. Do not arrive before 8:30am; no entry after noon.",checked="2026-11-09")])
RS="https://www.republicservices.com/municipality/southern-nevada/service-information"
metro("Las Vegas","Nevada","NV",[F("Republic Services HHW – North Las Vegas","333 W Gowan Rd (Gate B), North Las Vegas, NV 89032","Wed–Sat 9am–1pm on scheduled dates",RS,notes="Sites rotate; check 2026 HHW calendar"),F("Republic Services HHW – Henderson","560 Cape Horn Dr, Henderson, NV 89011","Wed–Sat 9am–1pm on scheduled dates",RS,notes="Sites rotate; check 2026 HHW calendar")])
metro("Atlanta","Georgia","GA",[F("CHaRM – Center for Hard to Recycle Materials","1110 Hill St SE, Atlanta, GA 30315","Tue & Thu 9am–2pm; Sat 8am–2pm, by appointment","https://livethrive.org/charm/location/","Household chemicals, paint, electronics, appliances, tires, mattresses, glass, metals, Styrofoam and more","Fees vary by item","Appointment only; 404-600-6386")])
HN="https://www.hennepincounty.gov/services/environment/hazardous-waste-households/drop-off-household-hazardous-waste-recycling"
metro("Minneapolis","Minnesota","MN",[F("Hennepin County Drop-off – Brooklyn Park","8100 Jefferson Hwy, Brooklyn Park, MN","Tue–Sat 9am–5pm",HN),F("Hennepin County Drop-off – Bloomington","1400 W 96th St, Bloomington, MN","Tue–Sat 9am–5pm",HN)])
MD="https://www.miamidade.gov/global/service.page?Mduid_service=ser1464798615648535"
metro("Miami","Florida","FL",[F("Home Chemical Collection Center – West Dade","8801 NW 58th St, Doral, FL 33178","Wed–Sun 9am–5pm",MD,notes="Residential only; no appointment"),F("Home Chemical Collection Center – South Dade","23707 SW 97th Ave, Gate B, Homestead, FL 33032","Wed–Sun 9am–5pm",MD,notes="Residential only; no appointment")])
metro("Tampa","Florida","FL",[F("Sheldon Road HHW Collection Center","9805 Sheldon Rd, Tampa, FL 33635","1st Sat 8am–2pm","https://hcfl.gov/locations/sheldon-road-household-hazardous-collection-center",notes="Photo ID with Hillsborough address"),F("South County HHW Collection","13000 US Hwy 41, Gibsonton, FL","2nd Sat 8am–2pm","https://hcfl.gov/residents/property-owners-and-renters/trash-and-recycling/discarding-household-hazardous-waste"),F("Hillsborough Heights HHW Collection Site","6209 County Road 579, Seffner, FL","3rd Sat 8am–2pm","https://hcfl.gov/locations/hillsborough-heights-household-hazardous-waste-collection-site")])
metro("Orlando","Florida","FL",[F("Porter Transfer Station HHW","1326 Good Homes Rd, Orlando, FL 32818","Mon–Sat 8am–5pm","https://www.orangecountyfl.net/watergarbagerecycling/householdhazardouswaste.aspx",fees="Free for Orange County residents",notes="Paint/chemicals max 25 gal per vehicle")])
metro("Baltimore","Maryland","MD",[F("Sisson Street Residential Recycling Center (HHW days)","2840 Sisson St, Baltimore, MD 21211","Collection days: Dec 4–5, 2026, 9am–5pm (Nov 6–7 already held)","https://www.baltimorecity.gov/publicworks/recycling-services/household-hazardous-waste-recycling",accepts="Automotive fluids, batteries, household cleaners, fungicides/herbicides, insecticides/pesticides, oil paint, thinners, pool chemicals, propane tanks, rust removers, solvents, fire extinguishers, thermometers, fluorescent bulbs",fees="Free",notes="Baltimore City residents only; materials in original labeled packaging; no commercial vehicles. 410-396-7250",checked="2026-11-09")])
metro("Sacramento","California","CA",[F("North Area Recovery Station HHW Drop-Off","4450 Roseville Rd, North Highlands, CA","Tue, Thu, Fri, Sat 8:30am–4pm","https://wmr.saccounty.gov/content/wmr/us/en/county-facilities/north-area-recovery-station/nars-hhw-drop-off.html")])
metro("Kansas City","Missouri","MO",[F("Household Hazardous Waste Facility","4707 Deramus Ave, Kansas City, MO 64120","Thu–Fri 9am–6pm; Sat 9am–4pm","https://www.kcwater.us/programs/hhw/",notes="No appointment under 600 lb; 816-513-8400")])
MM="https://www.mmsd.com/what-you-can-do/home-haz-mat-collection"
metro("Milwaukee","Wisconsin","WI",[F("MMSD South Drop Off Center","3879 W Lincoln Ave, Milwaukee, WI 53215","Thu–Sat 7am–3pm",MM,notes="Milwaukee County households"),F("MMSD 13th Street Drop Off","6060 S 13th St, Milwaukee, WI 53221","Tue 11am–6pm; Sat 8am–2pm",MM,notes="Milwaukee County households")])
metro("Oklahoma City","Oklahoma","OK",[F("Household Hazardous Waste Collection Center","1621 S Portland Ave, Oklahoma City, OK 73108","Tue–Fri 9:30am–6pm; Sat 8:30–11:30am","https://www.okc.gov/Services/Water-Trash-Recycling/Household-Hazardous-Waste-Collection-Center",notes="405-682-7038")])
metro("Louisville","Kentucky","KY",[F("Haz Bin","7501 Grade Ln, Louisville, KY 40219","Tue–Sat 9:30am–4pm","https://louisvilleky.gov/government/public-works/services/hazardous-materials-disposal-haz-bin")])
metro("Memphis","Tennessee","TN",[F("Shelby County HHW Facility","6305 Haley Rd, Memphis, TN 38134","Tue, Thu, Sat 8am–1pm","https://www.shelbycountytn.gov/439/Household-Hazardous-Waste",notes="Shelby County residents; 901-222-7729")])
metro("Albuquerque","New Mexico","NM",[F("HHW Collection Center (Safety-Kleen)","2720 Girard Blvd NE, Albuquerque, NM 87107","Mon, Wed, Fri 8am–2pm; Sat 8am–3pm","https://www.cabq.gov/solidwaste/hazardous-waste/household-hazardous-waste",fees="Free for City/Bernalillo County residents",notes="505-884-2277")])
metro("Tucson","Arizona","AZ",[F("Los Reales Sustainability Campus HHW","5300 E Los Reales Rd, Tucson, AZ 85756","Thu–Sat 7am–2pm (closed 2nd Sat except summer)","https://www.tucsonaz.gov/Departments/Environmental-Services/Household-Hazardous-Waste",fees="Free for Tucson residents; $15 for listed nearby residents",notes="Proof of residency")])
WK="https://www.wake.gov/departments-government/waste-recycling/facilities/household-hazardous-waste-facilities/"
metro("Raleigh","North Carolina","NC",[F("North Wake HHW Facility","9037 Deponie Dr, Raleigh, NC 27614","Sat 8am–4pm",WK+"north-wake-household-hazardous-waste-facility",notes="Wake County residents"),F("South Wake HHW Facility","6150 Old Smithfield Rd, Apex, NC 27539","Mon–Sat 8am–4pm",WK+"south-wake-household-hazardous-waste-facility",notes="Wake County residents"),F("East Wake HHW Facility","5051 Wendell Blvd, Wendell, NC 27591","Sat–Sun 8am–4pm",WK+"east-wake-household-hazardous-waste-facility",notes="Wake County residents")])
SL="https://www.saltlakecounty.gov/health/household-hazardous-waste/"
metro("Salt Lake City","Utah","UT",[F("Salt Lake County HHW Collection Center","8805 S 700 W, Sandy, UT 84070","Mon–Sat 7am–5pm",SL),F("Trans-Jordan Landfill HHW","10473 S Bacchus Hwy, South Jordan, UT","Mon–Sat 8am–5pm",SL),F("Salt Lake Valley Landfill HHW","6030 W California Ave, Salt Lake City, UT","Mon, Fri, Sat 7am–5pm",SL)])
metro("Omaha","Nebraska","NE",[F("Under The Sink","4001 S 120th St, Omaha, NE 68137","Wed 9am–4:45pm; Thu 9am–6:15pm; Fri 9am–4:45pm; Sat by appointment","https://www.underthesink.org/drop-off-info/location-hours/",notes="402-444-7465")])
metro("San Jose","California","CA",[F("Santa Clara County HHW – San Jose","1608 Las Plumas Ave, San Jose, CA 95133","Thu–Sat, by appointment","https://hhw.santaclaracounty.gov/drop-household-waste",fees="Free",notes="Appointment + proof of residency; (408) 299-7300")])
ST="https://www.hhwstl.com/locations"
metro("St. Louis","Missouri","MO",[F("St. Louis County HHW – South","291 E Hoffmeister Ave, St. Louis, MO 63125","Thu–Fri 8:30am–12pm & 1–5:30pm; select Sats",ST,notes="Reservation + proof of address"),F("St. Louis County HHW – North","4100 Seven Hills Dr, Florissant, MO 63033","Wed 8:30am–12pm & 1–5:30pm; select Sats",ST,notes="Reservation + proof of address")])
metro("Detroit","Michigan","MI",[F("ERG Environmental Services (Wayne County HHW)","13040 Merriman Rd, Livonia, MI 48150","Mon–Fri 9am–5pm","https://www.waynecountymi.gov/Government/Departments/Environmental-Services/Land-Resource-Management",fees="Free with Wayne County voucher (limited)")])
metro("Tulsa","Oklahoma","OK",[F("Household Pollutant Collection Facility","4502 S Galveston Ave, Tulsa, OK 74107","Wed & Sat 8–11:30am, noon–4:30pm","https://www.cityoftulsa.org/government/departments/public-works/household-pollutant-collection-facility/")])
RV="https://rcwaste.org/household-hazardous-waste"
metro("Riverside","California","CA",[F("Agua Mansa Permanent HHW Facility","1780 Agua Mansa Rd, Jurupa Valley, CA","Sat 9am–2pm","https://rcwaste.org/agua-mansa-permanent-hhw-facility"),F("Lake Elsinore HHW Facility","512 N Langstaff St, Lake Elsinore, CA","Sat; Oct–May 9am–2pm, Jun–Sep 7am–noon",RV),F("Palm Springs HHW Facility","1100 Vella Rd, Palm Springs, CA","Sat; Oct–May 9am–2pm, Jun–Sep 7am–noon",RV)])
metro("Virginia Beach","Virginia","VA",[F("Landfill & Resource Recovery Center HHW","1989 Jake Sears Rd, Virginia Beach, VA 23455","Tue–Sat 7am–4:30pm","https://pw.virginiabeach.gov/trash-recycling/landfill-and-rrc/household-hazardous-waste",notes="Proof of residency; 5 gal liquid or 75 lb per visit")])
metro("Pittsburgh","Pennsylvania","PA",[F("Noble Environmental HHW & Electronics Drop-off","3001 Railroad St, Pittsburgh, PA 15201","By appointment","https://www.pittsburghpa.gov/Resident-Services/Trash-Recycling/Drop-Off-Info-Additional-Resources/Electronic-Waste-and-Household-Hazardous-Waste-Disposal",HHW+"; electronics",notes="Appointment required")])
metro("Fresno","California","CA",[F("Environmental Compliance Center","1327 W Dan Ronquillo Dr, Fresno, CA 93706","Thu–Sat 9am–3pm","https://cleanupfresnocounty.com/drop-off-locations/",fees="Free",notes="(559) 600-4259")])
EP="https://www.elpasotexas.gov/environmental-services/collection-stations/"
metro("El Paso","Texas","TX",[F(f"Citizen Collection Station – {n}",a,"Tue–Sat 8am–4pm",EP,notes="Pass, current water bill and matching ID; 915-212-6000") for n,a in [("Northeast","4501 Hondo Pass Dr, El Paso, TX"),("Central","2492 Harrison Ave, El Paso, TX"),("Westside","121 Atlantic Rd, El Paso, TX"),("Mission Valley","1034 Pendale Rd, El Paso, TX"),("Eastside","3500 Confederate Dr, El Paso, TX")]])
metro("Cincinnati","Ohio","OH",[F("Cincinnati Recycling & Reuse Hub","911 Evans Street, Cincinnati, OH 45204","Tue 10am–2pm; Thu 12–6pm; Sat 10am–2pm (closed Nov 26–28 and Dec 22–Jan 1)","https://www.cincinnatirecyclingandreusehub.org/accepted-items",accepts="E-waste (computers, laptops, phones, printers, speakers, home entertainment, mixed electronics); TVs and monitors; car and bike tires (on or off rim) and bike inner tubes; batteries; lightbulbs (LED, CFL, tube)",fees="Electronics: small amounts free, car trunk $10 / SUV $15; TVs $5–$40; car tire off-rim $10 / on-rim $25; bike tire $5–$10",notes="Park on Woodrow Street (rear of building). Listed in Hamilton County Resource outlets directory. Household chemical HHW is NOT accepted here — county HHW is event-based.",checked="2026-11-09")],"Hamilton County's HHW chemical program is event-based with registration; no permanent public HHW site. Year-round tires and e-waste: Cincinnati Recycling & Reuse Hub. Source: https://hamiltoncountyresource.org/recycling_guide/hazardous_products.php")
CLE="https://www.clevelandohio.gov/city-hall/departments/public-works/divisions/waste/waste"
metro("Cleveland","Ohio","OH",[F("Carr Center (Division of Waste)","5600 Carnegie Ave., Cleveland, OH 44103","Recycling, shredding & computer/cell-phone disposal: Mon–Fri 9am–3pm. HHW: first Friday of each month only, 9am–3pm (next: Fri Dec 4, 2026)",CLE,accepts="E-waste: computers and cell phones (Mon–Fri; no TVs). HHW on first Fridays only: oil, cleaners, solvents, pesticides, household chemicals (latex paint not accepted)",fees="Free",notes="City of Cleveland residents only",checked="2026-11-09"),F("Ridge Road Transfer Station","3727 Ridge Rd., Cleveland, OH 44144","Recycling: Mon–Sat 9am–3pm. Regular waste disposal: Sat 9am–3pm. HHW: first Friday of each month only, 9am–3pm (next: Fri Dec 4, 2026). Bulky/tire drop-off for residents (limits apply)",CLE,accepts="Passenger tires without rims (residents; up to 4 free dumps/year including tires; fee beyond 4 tires); bulky waste; recycling; HHW on first Fridays only (oil, cleaners, solvents, pesticides, household chemicals; latex paint not accepted)",fees="Free for qualifying resident drop-offs; fee may apply beyond tire/dump limits",notes="City of Cleveland residents only; proof of residency required for drop-off",checked="2026-11-09")])
metro("Richmond","Virginia","VA",[F("East Richmond Road Convenience Center","3800 East Richmond Road, Richmond, VA 23223","Mon–Fri 7am–3:30pm; Sat 8:30am–2pm; closed Sun & holidays","https://www.rva.gov/public-works/trash-collection",accepts="Paints (20 gal/month/household), solvents, thinners, stains, varnish, motor oil, antifreeze, car fluids, lead-acid car batteries, cooking oil, fuels; passenger tires without rims (limit 4; no off-road or oversized)",fees="Free",notes="Richmond residents with proof of residency (license, utility bill, or registration). No pesticides, herbicides, fire extinguishers, asbestos, explosives. 804-646-4706",checked="2026-11-09"),F("Richmond Southside Transfer Station","3520 North Hopkins Road, Richmond, VA","Mon–Fri 6:30am–4:30pm; Sat 8:30am–2pm; closed Sun & holidays","https://www.rva.gov/public-works/trash-collection",accepts="Passenger tires without rims (limit 4 free; $1 each beyond 4; tractor-trailer tires $5 each); large bulk items, appliances, brush/yard waste; glass, cardboard, aluminum cans, newspapers",fees="Tires: 4 free then $1 each (passenger); tractor-trailer $5 each",notes="City residents; no commercial/contractor debris. 804-232-8488",checked="2026-11-09")])
metro("New Orleans","Louisiana","LA",[F("Recycling Drop-Off Center","2829 Elysian Fields Ave, New Orleans, LA","Saturdays 8am–1pm","https://nola.gov/recycling-drop-off/",accepts="E-waste (computers, laptops, phones, keyboards, monitors, printers, TVs limit 4, game consoles, cables, cameras); batteries (AA–D, 6V, 9V, lithium); light bulbs; tires (limit 5); glass (50 lbs); plastics #1–2; paper; cardboard; cans",fees="Free",notes="Orleans Parish residents only; businesses excluded. Household chemical HHW is annual Collection Day only (2026 was April 11).",checked="2026-11-09")])
metro("Honolulu","Hawaii","HI",[F("Kapaʻa Transfer Station","100 Kapaʻa Quarry Road, Kailua, HI","Mon–Fri 10am–6pm; Sat–Sun 7am–6pm (closed Christmas and New Year's Day)","https://www.honolulu.gov/env/ref/waste-drop-off-locations/",accepts="Household trash, bulky items, large appliances, tires, lead-acid batteries, standalone lithium/lithium-ion/NiMH/NiCad batteries, propane and helium tanks, butane, MAPP, fire extinguishers, green waste",fees="",notes="Phone (808) 768-4248. Residential drop-off rules apply.",checked="2026-11-09"),F("Kawailoa Transfer Station","62-180 Kawailoa Road, Haleiwa, HI","Daily 7am–6pm (closed Christmas and New Year's Day)","https://www.honolulu.gov/env/ref/waste-drop-off-locations/",accepts="Household trash, bulky items, large metal appliances, tires, lead-acid batteries, standalone lithium/lithium-ion/NiMH/NiCad batteries, propane and helium tanks, butane, MAPP, fire extinguishers, green waste",fees="",notes="Phone (808) 637-5511. Residential drop-off rules apply.",checked="2026-11-09")],"Household chemical HHW is appointment-only at city drop-off events (200-appointment cap). The last 2026 event (Sat Nov 7) is closed at capacity; 2027 dates TBD. Call (808) 768-3201 or email hhw@honolulu.gov. Source: https://www.honolulu.gov/env/ref/hhw-2/")
# --- Nov 10 2026 daily pass additions (each verified against cited official source on 2026-11-10) ---
def add(city,*fs):
    next(m for m in M if m["city"]==city)["facilities"].extend(fs)
D10="2026-11-10"
HEN="https://henrico.gov/services/public-use-areas-for-disposal/"
henacc="Passenger/automotive tires (tire trailer; up to 4 included in trip fee, max 6 per trip); free drop-off of used motor oil, old gasoline, antifreeze and oil-based paints & solvents; lead-acid batteries; recycling; yard waste"
henfee="$5 per trash/tire trip (includes up to 4 tires; $5 each beyond 4); HHW items (oil, gas, antifreeze, oil-based paint/solvents) free; recycling and yard waste free; $20 per refrigerant appliance"
hennote="Henrico County residents only (driver's license with Henrico address); no rental-property, vacant-lot or business waste. Closed New Year's Day, Independence Day, Thanksgiving, Christmas Eve and Christmas Day. (804) 727-8770. HHW program: https://henrico.gov/utility/solid-waste/household-hazardous-waste-disposal/"
add("Richmond",
  F("Henrico Springfield Road Public Use Area (West End)","10600 Fords Country Lane, Glen Allen, VA 23059","Daily 7:30am–7pm (closed listed holidays)",HEN,henacc,henfee,hennote,D10),
  F("Henrico Charles City Road Public Use Area (East End)","2075 Charles City Road, Henrico, VA 23231","Daily 7:30am–7pm (closed listed holidays)",HEN,henacc,henfee,hennote,D10))
JP="https://www.jeffparish.gov/1337/Drop-Off-Sites"
jpacc="Waste tires (5 per resident per day); motor oil (5 gal/day), oil filters (2/day), antifreeze (5 gal/day), gasoline (2 gal/day); lead-acid batteries; cooking oil (5 gal/day); e-waste: flat-screen TVs/monitors, computers, laptops, tablets, phones, printers, cable boxes, game consoles, networking gear, UPS units. Not accepted: CRT TVs/monitors, light bulbs, copiers, stereos, toner"
jpnote="Free self-service site for Jefferson Parish residents (driver's license or water bill required); commercial users may not drop off tires, auto fluids, e-waste or batteries. Unload items yourself. (504) 731-4612"
add("New Orleans",
  F("Jefferson Parish Metairie Drop-Off Site","400 David Drive, Metairie, LA 70003","Tue–Sun 9am–5:30pm (closed observed holidays)",JP,jpacc,"Free for residents",jpnote,D10),
  F("Jefferson Parish Marrero Drop-Off Site","6440 Lapalco Boulevard, Marrero, LA 70072","Tue–Sun 9am–5:30pm (closed observed holidays)",JP,jpacc,"Free for residents",jpnote,D10))
add("Honolulu",
  F("Keʻehi Transfer Station","606 Middle Street, Honolulu, HI","Mon–Fri 10am–6pm; Sat 7am–6pm; closed Sun, Christmas and New Year's Day","https://www.honolulu.gov/env/ref/waste-drop-off-locations/",
    "Lead-acid batteries; standalone lithium, lithium-ion, NiMH and NiCad batteries; household trash, combustible bulky items, metal items. NOT accepted: tires, large metal appliances, propane/helium/butane/MAPP tanks, fire extinguishers","",
    "Phone (808) 768-4884. For tires use Kapaʻa or Kawailoa Transfer Station.",D10))
add("Cleveland",
  F("Cuyahoga County Solid Waste District HQ (electronics drop-off bins)","4750 East 131 Street, Garfield Heights, OH 44105","Mon–Fri 8:30am–4:30pm; seasonal Special Saturdays (closed county holidays incl. Veterans Day, Thanksgiving, Christmas)","https://cuyahogarecycles.org/what_we_accept/",
    "Computer equipment, printers and peripherals; cell phones, tablets and handheld electronics (recycled by RET3 Job Corp.). NOT accepted: TVs, appliances, bulbs, batteries, smoke detectors","",
    "Open to Cuyahoga County residents; marked bins in the building vestibule; no bags or boxes; don't leave items outside after hours. (216) 443-3749",D10))
add("Louisville",
  F("Waste Reduction Center","636 Meriwether Avenue, Louisville, KY 40217 (entrance on Bland Street)","Tue–Fri 8am–12pm & 1–4:30pm; Sat 8am–3pm","https://louisvilleky.gov/government/public-works/waste-reduction-center",
    "Passenger car tires (up to 4/day free for residents); electronics (up to 3 items/day free for residents; computers, monitors, TVs, printers, phones, game systems); up to 4 large household items/day; truck tires (fee)",
    "Residents: 4 tires, 3 electronics and 4 large items per day free; business passenger tires $4 each; truck tires $10 ($25 on rims); extra electronics $0.60/lb by appointment; debit/credit only",
    "Louisville/Jefferson County residents and businesses; holidays may change hours (closed Thanksgiving Day and day after). 502-574-2796",D10))
for m in M:
    if m["city"]=="Honolulu":
        m["note"]="Household chemical HHW is appointment-only at city drop-off events (200-appointment cap). The final 2026 event was held Sat Nov 7; 2027 dates are TBD. Call (808) 768-3201 or email hhw@honolulu.gov. Source: https://www.honolulu.gov/env/ref/hhw-2/ (checked 2026-11-10)"
    if m["city"]=="San Antonio":
        m["note"]=m["note"].replace("(re-verified 2026-11-09)","(re-verified 2026-11-10). Later dates: Sat Feb 13, Apr 10 and Jul 10, 2027, 8am–1pm")
    for f in m["facilities"]:
        if m["city"] in("Washington","Boston","Baltimore") and f["checked"]=="2026-11-09" and ("Event" in f["hours"] or "Collection days" in f["hours"]):
            f["checked"]=D10
# --- Nov 11 2026 daily pass additions (each verified against cited official source on 2026-11-11) ---
D11="2026-11-11"
DAL="https://dallascityhall.com/departments/sanitation/Pages/Landfill-and-Transfer-Stations.aspx"
daltire="Tires (limit 6 per year from Dallas residents, not exceeding 25 inches in diameter); electronics (residents only)"
dalfree="Free for Dallas residents in passenger cars, station wagons, pickups and trailers under 15 ft hauling their own residential waste"
dalid="valid driver's license plus proof of Dallas residency (Dallas address on the license or a current Dallas water bill)"
add("Dallas",
  F("McCommas Bluff Landfill","5100 Youngblood Road, Dallas, TX","Mon–Fri 5am–8pm; Sat 6am–4pm; closed Sun","https://dallascityhall.com/departments/sanitation/pages/mccommas_bluff.aspx",
    daltire+"; household waste, furniture, appliances (refrigerants removed), grass clippings/brush",dalfree+"; commercial customers pay posted rates; uncovered loads $40",
    "Open to commercial and residential customers. Residents: current, valid Texas driver's license showing a Dallas address or a current Dallas water utilities bill. (214) 670-0977",D11),
  F("Northwest (Bachman) Transfer Station","9500 Harry Hines Boulevard, Dallas, TX","Mon–Sat 7am–4:30pm; closed Sun","https://dallascityhall.com/departments/sanitation/Pages/northwest_bachman.aspx",
    daltire+"; recyclables, scrap metal, household waste, grass clippings. NOT accepted: chemicals, paint and other hazardous waste; refrigerators, freezers, AC units",dalfree,
    "Open only to Dallas residents and small commercial customers; "+dalid+". (214) 670-6161",D11),
  F("Northeast (Fair Oaks) Transfer Station","7677 Fair Oaks Avenue, Dallas, TX","Temporarily closed Oct 28–Nov 15, 2026 (reopens Mon Nov 16); then Mon–Fri 7am–9am; Sat 7am–4pm; closed Sun",DAL,
    daltire+"; recyclables, scrap metal, household waste, furniture, grass clippings/brush",dalfree,
    "Dallas residents only; no commercial customers; "+dalid+". During the closure use another transfer station or McCommas Bluff Landfill. (214) 670-6126",D11),
  F("Southwest (Westmoreland) Transfer Station","4610 S. Westmoreland Road, Dallas, TX","Temporarily closed Oct 14–Nov 15, 2026 (reopens Mon Nov 16); then Mon–Fri 7am–9am; Sat 7am–4pm; closed Sun",DAL,
    daltire+"; recyclables, scrap metal, household waste, furniture, grass clippings/brush",dalfree,
    "Dallas residents only; no commercial customers; "+dalid+". During the closure use another transfer station or McCommas Bluff Landfill. (214) 670-1927",D11))
CHE="https://www.chesterfield.gov/539/Convenience-Centers"
cheacc="Tires (limit 5; oversized tires not accepted); used motor oil, antifreeze and residential oil filters (10 gal per visit); electronics and TVs (go in the trash containers for a $9 fee; recycle them at county e-cycling events instead); 1 lb and 20 lb propane tanks (limit 5); appliances; household trash; recyclables. NOT accepted: oil-based paint (county events only), fire extinguishers, propane tanks over 30 lb"
chefee="Tires $2 each off-rim, $5 each on-rim; used oil and antifreeze free; electronics/TVs $9; trash or yard debris $9 per pickup load; Freon appliances $15, other appliances $10"
chenote="Chesterfield County residents; be prepared to show ID/proof of county residency. Closed Veterans Day (Nov 11), Thanksgiving and the day after (Nov 26–27), Christmas Eve and Day; closes at noon Dec 31. Card or cash ($1–$50 bills). 804-748-1297"
add("Richmond",
  F("Chesterfield Northern Area Convenience Center","3200 Warbro Road, Midlothian, VA 23112","Daily 7am–6pm (closed listed county holidays)",CHE,cheacc,chefee,chenote,D11),
  F("Chesterfield Southern Area Convenience Center","6700 Landfill Drive, Chester, VA 23831","Daily 7am–6pm (closed listed county holidays)",CHE,cheacc,chefee,chenote,D11))
HNLCC="https://www.honolulu.gov/env/ref/waste-drop-off-locations/"
hnlacc="Passenger or light truck tires, with or without rims (limit 4 per month); household rubbish, furniture, bulky items, large metal appliances (limit 2 per month), green waste. NOT accepted: heavy truck or equipment tires"
hnlnote="Residents only (no businesses); sedans, SUVs, pickups or minivans only, no trailers; 2 loads per day. Rules: https://www.honolulu.gov/env/ref/opala2-waste-drop-off-rules-residents/"
add("Honolulu",
  F("Waipahu Convenience Center","94-071 Waipahu Depot Street, Waipahu, HI","Daily 7am–6pm (closed Christmas and New Year's Day)",HNLCC,hnlacc,"",hnlnote+". Phone (808) 676-8878",D11),
  F("Kapolei Convenience Center","91-184 Kaomi Loop, Kapolei, HI","Daily 7am–6pm (closed Christmas and New Year's Day)",HNLCC,hnlacc,"",hnlnote+". Phone (808) 260-2801",D11))
# Re-verified against the official page on 2026-11-11 (no listing text changed).
REVERIFIED={"DPW Special Waste Collection Event – RFK Stadium Lot 8","Zero Waste Day Drop-Off – Millennium Park","Sisson Street Residential Recycling Center (HHW days)","Carr Center (Division of Waste)","Ridge Road Transfer Station","Kapaʻa Transfer Station","Kawailoa Transfer Station","Keʻehi Transfer Station"}
for m in M:
    for f in m["facilities"]:
        if f["name"] in REVERIFIED or f["name"].startswith("Bulky Waste Collection Center –"): f["checked"]=D11
    if m["city"]=="San Antonio": m["note"]=m["note"].replace("(re-verified 2026-11-10)","(re-verified 2026-11-11)")
# --- Nov 12 2026 daily pass additions (each verified against cited official source on 2026-11-12) ---
D12="2026-11-12"
hnlacc_nogreen=hnlacc.replace(", green waste. NOT accepted:",". No green waste at this site. NOT accepted:")
add("Honolulu",
  F("Waimānalo Convenience Center","41-241 Hihimanu Street, Waimānalo, HI","Daily 7am–6pm (closed Christmas and New Year's Day)",HNLCC,hnlacc,"",hnlnote+". Phone (808) 259-7182",D12),
  F("Waiʻanae Convenience Center","85-572 Waiʻanae Valley Road, Waiʻanae, HI","Daily 7am–6pm (closed Christmas and New Year's Day)",HNLCC,hnlacc,"",hnlnote+". Phone (808) 696-4203",D12),
  F("ʻEwa Beach Convenience Center","91-1000 Geiger Road, ʻEwa Beach, HI","Daily 7am–6pm (closed Christmas and New Year's Day)",HNLCC,hnlacc,"",hnlnote+". Phone (808) 226-2996",D12),
  F("Lāʻie Convenience Center","56-020 Kamehameha Highway, Lāʻie, HI","Daily 7am–6pm (closed Christmas and New Year's Day)",HNLCC,hnlacc,"",hnlnote+". Phone (808) 293-8714",D12),
  F("Wahiawā Convenience Center","71-129 Wilikina Drive, Wahiawā, HI","Daily 7am–6pm (closed Christmas and New Year's Day)",HNLCC,hnlacc_nogreen,"",hnlnote+". Phone (808) 621-3648",D12))
HAN="https://www.hanovercounty.gov/225/Residential-Only-Trash-Center-Hours-and-"
hanacc="Passenger vehicle tires up to 32 in. diameter (4 per day, no fee); used oil, oil filters, antifreeze, gasoline, automobile fluids and solvents; lead-acid batteries; household trash, bulky waste (furniture, appliances), recyclables, clothing. Liquid paint is not accepted for recycling (dry it to a paste and place it in the trash); electronics go to the county's e-waste collection events (typically spring and fall)"
hanfee="No cost for residents' household trash and recyclables; up to 4 passenger tires per day without fee"
hannote="Hanover County residents only; bring ID or vehicle registration (staff may verify residency). No commercial vehicles, U-Hauls or box trucks; businesses must use the Route 301 Transfer Station. Closed New Year's Day, MLK Day, Presidents Day, Easter Sunday, Memorial Day, Juneteenth, Independence Day, Labor Day, Veterans Day, Thanksgiving and the day after, Christmas Eve and Christmas Day. Call Before You Haul: 804-365-3388. Tires/batteries/paint details: https://www.hanovercounty.gov/230/What-Can-Be-Recycled"
add("Richmond",
  F("Hanover Mechanicsville Convenience Center","7427 Verdi Lane, Mechanicsville, VA 23116","Daily 7am–7pm (closed listed county holidays)",HAN,hanacc+"; grass, unbagged leaves and brush (up to 4 in. thick, 6 ft long; no bamboo); Goodwill donations",hanfee,hannote,D12),
  F("Hanover Courthouse Convenience Center","7234 Courtland Farm Road, Hanover, VA 23069","Daily 7am–7pm (closed listed county holidays)",HAN,hanacc+"; grass and unbagged leaves; mattresses and box springs (limit 2 per day)",hanfee,hannote,D12),
  F("Hanover Elmont Convenience Center","11045 Lewistown Road, Ashland, VA 23005","Daily 7am–7pm (closed listed county holidays)",HAN,hanacc+"; grass and unbagged leaves",hanfee,hannote,D12))
# Re-verified against the official page on 2026-11-12 (no listing text changed).
REVERIFIED12={"DPW Special Waste Collection Event – RFK Stadium Lot 8","Zero Waste Day Drop-Off – Millennium Park","Sisson Street Residential Recycling Center (HHW days)","Kapaʻa Transfer Station","Kawailoa Transfer Station","Keʻehi Transfer Station","Waipahu Convenience Center","Kapolei Convenience Center","Chesterfield Northern Area Convenience Center","Chesterfield Southern Area Convenience Center"}
for m in M:
    for f in m["facilities"]:
        if f["name"] in REVERIFIED12 or f["name"].startswith("Bulky Waste Collection Center –"): f["checked"]=D12
    if m["city"]=="San Antonio": m["note"]=m["note"].replace("(re-verified 2026-11-11)","(re-verified 2026-11-12)")
# --- Nov 13 2026 daily pass additions (each verified against cited official source on 2026-11-13) ---
D13="2026-11-13"
add("Richmond",
  F("Hanover Beaverdam Convenience Center","18400 Beaverdam Road, Beaverdam, VA 23015","Daily 7am–7pm (closed listed county holidays)",HAN,hanacc,hanfee,hannote,D13),
  F("Hanover Doswell Convenience Center","11224 Doswell Road, Doswell, VA 23047","Daily 7am–7pm (closed listed county holidays)",HAN,hanacc,hanfee,hannote,D13),
  F("Hanover Montpelier Convenience Center","15188 Clazemont Road, Montpelier, VA 23192","Daily 7am–7pm (closed listed county holidays)",HAN,hanacc+"; mattresses and box springs (limit 2 per day)",hanfee,hannote,D13))
CUY="Cuyahoga County Solid Waste District HHW program (Ohio): free to all Cuyahoga County households; examples include oil- or solvent-based paint, solvents, automotive fluids, aerosols, pesticides, pool chemicals and household cleaners. The District's own facility is not open to the public."
add("Cleveland",
  F("Maple Heights Service Garage (HHW drop-off)","5501 Dunham Road, Maple Heights, OH","Year-round, Mon–Fri 8am–3pm","https://cuyahogarecycles.org/recycle-in/maple-heights/household_hazardous_waste/",
    "Household hazardous waste (oil-based paint, solvents, automotive fluids, aerosols, pesticides, pool chemicals, household cleaners). No latex paint","Free (Cuyahoga County HHW program)",
    "Maple Heights residents only. "+CUY,D13),
  F("Warrensville Heights Service Garage (HHW drop-off)","19700 Miles Avenue, Warrensville Heights, OH","Year-round, Mon–Fri 8am–3pm","https://cuyahogarecycles.org/recycle-in/warrensville-heights/household_hazardous_waste/",
    "Household hazardous waste (oil-based paint, solvents, automotive fluids, aerosols, pesticides, pool chemicals, household cleaners). Latex paint accepted","Free (Cuyahoga County HHW program)",
    "Drop-off is at the city service garage; the District says most communities accept waste only from their own residents, so call the city before going. "+CUY,D13))
add("New Orleans",
  F("Gretna Burmaster Waste Drop-Off Site","1201 Burmaster Street, Gretna, LA 70053","Tue–Sat 7:30am–4pm; closed Sun–Mon","https://www.gretnala.com/waste-drop-off-site/",
    "Bulk items: tree debris, furniture, appliances, miscellaneous trash, motor oil. NOT accepted: hazardous waste, tires, batteries, fuel, non-motor oil, electronics",
    "Free to Gretna residents; $35 gate fee for contractors and residents with small trailers (6 ft or less)",
    "Operated by the City of Gretna. Replaced Jefferson Parish's Meadowbrook Drop-Off Site (484 Wall Blvd) on Nov 3, 2026; through a parish partnership all Jefferson Parish residents may use it free for residential waste (https://www.jeffparish.gov/1337/Drop-Off-Sites). City contact 504-363-1500",D13))
NSCC="https://www.nashville.gov/departments/waste-services/convenience-centers"
add("Nashville",
  F("Omohundro Convenience Center","1019 Omohundro Pl, Nashville, TN 37210","Tue–Sat 8:30am–4:30pm (closed Metro holidays)",NSCC,
    "Electronics (free, up to 100 lb per visit); cooking grease; mattresses and box springs ($12 each, 4 per month); construction and demolition material ($20, up to 2 cu yd); 3 bags of household trash plus 1 bulk item free; recycling and compostables. Household hazardous waste and tires go to East or Ezell Pike",
    "Electronics, recycling and 3 bags + 1 bulk item free; other loads $10 under 1 cu yd or $20 per cu yd; card fee 2.8% (min $1.95); cash not accepted here",
    "Davidson County residents only; show a Tennessee driver's license with a Davidson County address. No commercial vehicles or commercial waste. Hours/locations: https://www.nashville.gov/departments/waste-services/convenience-centers/hours-and-locations",D13))
# Nashville East/Ezell: convenience-center fee table (official) adds electronics and tires; re-verified 2026-11-13.
nsx="; electronics (free, up to 100 lb per visit); tires without rims (free, 4 per month; $5 per tire with rims)"
for m in M:
    if m["city"]=="Nashville":
        for f in m["facilities"]:
            if f["name"] in ("East Convenience Center","Ezell Pike Convenience Center"):
                f["accepts"]=HHW+nsx; f["checked"]=D13
# Re-verified against the official page on 2026-11-13 (no listing text changed).
REVERIFIED13={"DPW Special Waste Collection Event – RFK Stadium Lot 8","Zero Waste Day Drop-Off – Millennium Park","Sisson Street Residential Recycling Center (HHW days)","Hanover Mechanicsville Convenience Center","Hanover Courthouse Convenience Center","Hanover Elmont Convenience Center"}
for m in M:
    for f in m["facilities"]:
        if f["name"] in REVERIFIED13: f["checked"]=D13
    if m["city"]=="San Antonio": m["note"]=m["note"].replace("(re-verified 2026-11-12)","(re-verified 2026-11-13)")
# --- Nov 14 2026 daily pass additions (each verified against cited official source on 2026-11-14) ---
D14="2026-11-14"
PHL="https://www.phila.gov/services/trash-recycling-city-upkeep/find-a-sanitation-convenience-center-to-drop-off-trash-or-recycling/"
phlacc="Automotive tires (limit 4 per day); electronic waste including computers, monitors and televisions; latex or water-based paint (must be solidified with an absorbent such as kitty litter or newspaper); fluorescent light bulbs; lithium, rechargeable and lead-acid batteries; bulk items, large metal household items and appliances incl. items with refrigerants (limit 2 per day); mattresses and box springs (unwrapped); trash (up to 6 receptacles or 12 bags); recyclables; yard waste (paper bags only); Christmas trees. NOT accepted: construction debris"
phlfee="Free (Streets Department: “there is no charge to drop-off materials”)"
phlnote="Philadelphia residents only; present proof that you live in Philadelphia. Regular household items once a day, oversized items once a week. Personal or commercial vehicles under 6,000 lb total vehicle weight; commercial contractors and commercial loads not allowed. Closed City holidays. Address and phone from the City’s Recycling and Donation Finder"
add("Philadelphia",*[F(f"Sanitation Convenience Center – {n}",a,"Mon–Sat 8am–6pm (closed City holidays)",PHL,phlacc,phlfee,phlnote+f"; {ph}",D14) for n,a,ph in [
  ("Port Richmond","3901 Delaware Ave, Philadelphia, PA 19137","(215) 685-1358"),
  ("Northwest Philadelphia","320 Domino Ln, Philadelphia, PA 19128","(215) 685-2502"),
  ("Northeast Philadelphia","8401 State Rd, Philadelphia, PA 19136","(215) 685-8072"),
  ("Southwest Philadelphia","3033 S 63rd St, Philadelphia, PA 19153","(215) 685-4290"),
  ("Strawberry Mansion","2601 W Glenwood Ave, Philadelphia, PA 19121","(215) 685-3955"),
  ("West Philadelphia","5100 Grays Ave, Philadelphia, PA 19143","(215) 685-2600")]])
for m in M:
    if m["city"]=="Philadelphia":
        m["note"]=m["note"].replace("take them to a Sanitation Convenience Center.","take them to one of the six Sanitation Convenience Centers listed here.")
add("Cleveland",
  F("Lakewood Service Garage (HHW drop-off)","12920 Berea Road, Lakewood, OH","Year-round, Mon–Fri 8am–2pm; Sat 8am–12pm","https://cuyahogarecycles.org/recycle-in/lakewood/household_hazardous_waste/",
    "Household hazardous waste (oil-based paint, solvents, automotive fluids, aerosols, pesticides, pool chemicals, household cleaners). No latex paint","Free (Cuyahoga County HHW program)",
    "Lakewood residents only. "+CUY,D14),
  F("South Euclid Service Garage (HHW drop-off)","4224 Monticello Boulevard, South Euclid, OH","Year-round, Mon–Fri 8am–3pm","https://cuyahogarecycles.org/recycle-in/south-euclid/household_hazardous_waste/",
    "Household hazardous waste (oil-based paint, solvents, automotive fluids, aerosols, pesticides, pool chemicals, household cleaners). No latex paint","Free (Cuyahoga County HHW program)",
    "Drop-off is at the city service garage; the District says most communities accept waste only from their own residents, so call the city before going. "+CUY,D14))
# Re-verified against the official page on 2026-11-14 (no listing text changed).
REVERIFIED14={"DPW Special Waste Collection Event – RFK Stadium Lot 8","Zero Waste Day Drop-Off – Millennium Park","Sisson Street Residential Recycling Center (HHW days)"}
for m in M:
    for f in m["facilities"]:
        if f["name"] in REVERIFIED14: f["checked"]=D14
    if m["city"]=="San Antonio": m["note"]=m["note"].replace("(re-verified 2026-11-13)","(re-verified 2026-11-14)")
# Stable facility URLs and reviewed answers live in a separate source-backed seed file.
# A changed listing invalidates old answers instead of silently carrying them forward.
import hashlib, re
from facility_questions import unknown_questions
DETAILS=json.load(open("data/facility_details.json"))
for m in M:
    for f in m["facilities"]:
        key=m["st"]+"|"+m["city"]+"|"+f["name"]
        detail=DETAILS.get(key,{})
        f["slug"]=detail.get("slug") or re.sub(r"[^a-z0-9]+","-",f["name"].lower()).strip("-")
        fingerprint=hashlib.sha256(json.dumps({k:f[k] for k in ["accepts","fees","notes","hours"]},sort_keys=True).encode()).hexdigest()
        fresh=(detail.get("listing_fingerprint")==fingerprint and detail.get("source")==f["source"] and detail.get("source_checked")==f["checked"])
        f["questions"]=detail["questions"] if fresh else unknown_questions()
        f["operator"]=detail.get("operator","not stated by source") if fresh else "not stated by source"
        if fresh:
            f.update(detail.get("source_fields",{}))
            f["source_notice"]=detail.get("source_notice", "")
            f["questions_reviewed"]=detail.get("questions_reviewed",f["checked"])
json.dump(M,open("data/facilities.json","w"),indent=1,ensure_ascii=False)
print(len(M),"metros",sum(len(m["facilities"]) for m in M),"facilities")
