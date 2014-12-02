from datetime import datetime
import pickle, re

# load data
f = open('extractItems' + '/extractData.p', 'rb')
houses = pickle.load(f)
f.close()
    
def stripAnchor(data):
    "strip <*>  <*>"
    num = None
    if '>' in data or '<' in data:
        data = re.search('>(.*?)<', data)
        if data is not None and data.group(1) != '':
            num = data.group(1).strip()
    return num

def ifExit(data):
    if data:
        return 1
    else:
        return None
        
def ifIn(data, x):
    num = None
    if data is not None and x in data:
        num = 1
    return num 
        
def getNum(data):
    if data is None:
        return None
    num = None
    match = re.search('[\d,.]+', data)
    if match:
        num = match.group()
    if ',' in num:
        num = float(num.replace(',', ''))  
    if num is not None:
        num = float(num)
    return num

# x Hour(s) Ago, x Day(s) Ago, x Weeks Ago, x Months Ago, x Years Ago
def dateToNum(date):
    "convert all to days"
    if date is None:
        return None
    x = (date.split(' ')[0]).strip()
    if len(x):
        x = int(x)
    if 'Hour' in date:
        x = x/24.0
    elif 'Week' in date:
        x = 7*x
    elif 'Month' in date:
        x = 30*x
    elif 'Year' in date:
        x = 365*x
    return x

# split "condo Info" into "Condo/Coop" and "Condo/Coop Fee"
def condoInfo(data):
    x = {"Condo/Coop": None, "Condo/Coop Fee": None}
    if 'Condo/Coop: ' in data[0]:
        x["Condo/Coop"]= data[0].split(': ')[1].strip()
    if len(data)>1 and 'Condo/Coop Fee' in data[1]:
        x["Condo/Coop Fee"] =data[1].split()[0][1:]
    return x["Condo/Coop"], x["Condo/Coop Fee"]
                   
# convert Acres to sq ft, 1 Acres = 43560 Sq Ft
def acres2sqft(data):
    if data is None:
        return None
    area = 0
    match = re.search('[\d,.]+', data)
    if match:
        area = match.group()
    if ',' in area:
        area = float(area.replace(',',''))
    if 'Acres' in data:
        area = float(area)*43560
    return area

def bath(data):
    num = None
    pat = re.compile('(?P<full>[\d]+) Full, (?P<half>[\d]+) Half Bath|(?P<all>[\d]+) Full Bath')
    match = pat.search(data)
    if match:
        num = match.groupdict()
        if num['all'] is None:
            num['all'] = float(num['full'] or 0) + float(num['half'] or 0)*0.5
            return float(num['all'])
    else:
        return num

def propertyType(data):
    # None = 'Unknown', 1 = 'Single Family Home',  2 = 'Condo/Townhome/Row Home/Co-Op',3 = 'Land',4 = 'Farms/Ranches'
    if data is None:
        return None
    num = 0
    if data == 'Single Family Home':
        num = 1
    elif data == 'Condo/Townhome/Row Home/Co-Op':
        num = 2
    elif data == 'Land':
        num =3
    elif data == 'Farms/Ranches':
        num =4
    return num
	
class Rooms:
    "store bedrooms information"
    def __init__(self, beds = None, bedrooms = None, otherrooms = None, baths = None, bathrooms = None):
        self.beds = None
        self.bedsOnMain = None
        self.bedsOnUpper = None
        self.basement = None
        self.baths = None
        if beds is not None and len(beds) > 0 :
            self.beds = int(beds[0])
        
        if bedrooms is not None and len(bedrooms) > 1:
            if 'Main Floor' in bedrooms[1]:
                self.bedsOnMain = int(bedrooms[1][0])
            if 'Upper Floor' in bedrooms[1]:
                self.bedsOnUpper = int(bedrooms[1][0])
        if self.beds is not None:
            if self.bedsOnMain is not None:
                self.bedsOnUpper = self.beds - self.bedsOnMain
            if self.bedsOnUpper is not None:
                self.bedsOnMain = self.beds - self.bedsOnUpper
        if baths is not None:
            self.baths = bath(baths)

def stories(data):
    num = None
    try:
        for item in data:
            if 'Stories' in item:
                try:
                    num = int(item[0])
                except:
                    pass
        return num
    except:
        return num
  
def status(data):
    "1 = 'Active', 2 = 'Ready to build', 3 = 'Cntg/No Ko', 4 = 'Cntg/Ko'" 
    num = None    
    if data:
        if data == 'Active':
            num = 1
        elif data == 'Ready to build':
            num = 2
        elif data == 'Cntg/No Ko':
            num = 3
        else:
            num =4
    return num
    
def houseCleaned(house):
    '''
    clean & store house items into a table
    
    #Discard the following items
    "# of Units": only one result(6 units)
    "Community" : too few
    "Farm Info" : ifExit(), find only one result
    "Garage/Parking": only 1 result ['2 car garage(s)']
    "Legal and finance": only two results
    "Location" : just two results['Area:  Montgomery', 'Subdivision:  Tanglewood')]
    "MLS": all results are ['Washingtondc']
    "Multi-Unit Info" : only one results
    "Neighborhood": only 7 results [Wheaton, Aspen Hill, Fairland]
    "Other Property Info", no meaningful information is found
    "Rental Info" : only 3 results
    "Room Description": only two results 
    "School Information": redundant
    "School": redundant
    "Special Promotions", completely no infomation
    "Unit Features": only 2 results
    "View" : only one results
    "Utilities", most of them are ['Public Water', 'Public Sewer']
    
    #Mapping Functions & description
    #create a cleaned list for each house, defaults None
    [0] "Address" : string            
    [1] "Accessibility Features": ifIn(house["Accessibility Features"], 'Elevator')   # if Elevator is in 1, otherwise None
    [2] "Added to Site": str(datetime.strptime(x, '%B %d, %Y').date())
    [3] "Amenities and Community Features": len(house["Amenities and Community Features"]) # count the number of Amenities and Community Features
    [4] "Appliances" : len(house['Appliances']) # count the number of Appliances
    [5]-[9] "Bathrooms" and "Baths", "Bedrooms" and "Beds", and "Other rooms" : ### use Class Rooms()
    [10] "Brokeredby" : string, company names
    [11] "Builder" :  string, company names
    [12] "Stories": int(house.get("Stories")[0][0])
    [13]-[14] "Condo Info" : condoInfo()
    [15] "Garage" : int(house['Garage'][0])
    [16]-[17] "Heating and Cooling":  ifIn(data, 'Electric Cooling'), ifIn(data, 'Central A/C')                                
    [18]-[19] "Homeowners Association": ifIn(data, 'Parking Included In List Price')
                                        ifIn(data, 'HOA: $') --> getNum(data)
    [20] "House Size" : getNum()
    [21] "Last refreshed" : dateToNum()
    [22] "Listing Agent" : string, agent names
    [23] "Lot Size": acres2sqft('0.54 Acres')
    [24] "MLS ID": int(MLS ID[2:]) ,MC8446433 
    [25] "Pool and Spa" : ifExit(),                
    [26] "PostalCode": int(house["PostalCode"])  
    [27] "Price/sqft": getNum(house['Price/sqft'])
    [28] "Property Status" : ifExit()  #Ready to build
    [29] "Property Type" : propertyType(house.get('Property Type')),\
        'None' = 'Unknown', 1 = 'Single Family Home',  2 = 'Condo/Townhome/Row Home/Co-Op',\
        3 = 'Land',4 = 'Farms/Ranches'
    [30] "Status" : status(house.get("Status")), 'None' = 'Unkown', 1 = 'Active', 2 = 'Ready to build', 3 = 'Cntg/No Ko', 4 = 'Cntg/Ko'" 
    [31] "Style" : stripAnchor(house.get("Style")), 28 different styles
    [32] "Year Built" : int(house["Year Built"])
    [33] "Price" : number,
    '''

    houseItems = [None,]*34
    houseItems[0] = house.get('Address')
    houseItems[1] = ifIn(house.get("Accessibility Features"), 'Elevator')
    if "Added to Site" in house: 
        houseItems[2] = str(datetime.strptime(house["Added to Site"], '%B %d, %Y').date())
    if "Amenities and Community Features" in house:
        houseItems[3] = len(house["Amenities and Community Features"])
    if "Appliances" in house:
        houseItems[4] = len(house['Appliances'])      
    bedx = Rooms(house.get("Beds"), house.get("Bedrooms"),house.get("Other rooms"),house.get("Baths"), house.get("Bathrooms"))
    houseItems[5] = bedx.beds
    houseItems[6] = bedx.bedsOnMain
    houseItems[7] = bedx.bedsOnUpper
    houseItems[8] = bedx.baths
    houseItems[9] = bedx.basement
    houseItems[10] = house.get("Brokeredby")
    houseItems[11] = house.get("Builder")
    x = house.get("Stories")    
    if isinstance(x, list):
        x = x[0][0]   
        houseItems[12] = int(x)
    if "Condo Info" in house:
        temp = condoInfo(house.get("Condo Info"))
        houseItems[13], houseItems[14] = temp
    if house.get('Garage'):
        houseItems[15] =  int(house.get('Garage')[0])
    houseItems[16] = ifIn(house.get("Heating and Cooling"), 'Electric Cooling')
    houseItems[17] = ifIn(house.get("Heating and Cooling"), 'Central A/C')
    houseItems[18] = ifIn(house.get("Homeowners Association"), 'Parking Included In List Price')
    if house.get("Homeowners Association"):
        for line in house.get("Homeowners Association"):
            if ifIn(line, 'HOA: $'):
                houseItems[19] = getNum(line)
    houseItems[20] = getNum(house.get("House Size"))
    houseItems[21] = dateToNum(house.get("Last refreshed")) 
    houseItems[22] = house.get("Listing Agent")
    houseItems[23] = acres2sqft(house.get("Lot Size"))
    houseItems[24] = int(house.get("MLS ID", "MC0")[2:])
    houseItems[25] = ifExit(house.get("Pool and Spa"))
    if house.get("PostalCode"):
        houseItems[26] = int(house["PostalCode"])
    houseItems[27] = getNum(house.get("Price/sqft"))
    houseItems[28] = ifExit(house.get("Property Status"))
    houseItems[29] = propertyType(house.get('Property Type'))
    houseItems[30] = status(house.get("Status")) 
    houseItems[31] = stripAnchor(house.get("Style", '><'))
    if house.get("Year Built"):
        houseItems[32] = int(house.get("Year Built"))  
    houseItems[33] = getNum(house["Price"])
    # convert all the items into string and add '\t' between them    
    strItems = ''
    for l in houseItems:
        strItems += str(l) + '\t'
     
    return strItems

header = ['Address(String)',	'Elevator(Numerical)',	'AddedToSite(Date)', \
    'AmenitiesCommunity(Numerical)', 'Appliances(Numerical)', 'Beds(Numerical)', 'BedsOnMain(Numerical)',\
    'BedsOnUpper(Numerical)', 'Baths(Numerical)', 'Basement(Numerical)', 'Brokeredby(String)', \
    'Builder(String)', 'StoriesNum(Numerical)', 'CondoCoop(String)',	'CondoCoopFee(Numerical)', \
    'Garage(Numerical)', 'ElectCooling(Categorical)', 'CentralAC(Categorical)',	'ParkingInPrice(Categorical)', \
    'HOAFee(Numerical)', 'HouseSize(Numerical)', 'Lastrefreshed(Numerical)', 'ListingAgent(String)', \
    'LotSize(Numerical)', 'MLSID(Categorical)', 'PoolSpa(Categorical)', 'PostalCode(Categorical)', \
    'PriceSqFt(Numerical)', 'PropertyStatus(Categorical)', 'PropertyType(Categorical)', \
    'Status(Categorical)', 'Style(String)', 'YearBuilt(Numerical)', 'Price(Numerical)', ]

fTab = open('extractItems' + '/houses.txt', 'w')

strHeader =''    
for l in header:
    strHeader += l + '\t'
fTab.write(strHeader+'\n')
    
for house in houses:
    fTab.write(str(houseCleaned(house)) + '\n')
        
fTab.close()