import os, re
from datetime import datetime

outFolder='extractItems'

if not os.path.exists(outFolder):
    os.mkdir(outFolder) 
    
# if the file exist, delete it firstly
try:
    os.remove(outFolder + '/extractData.txt')
except OSError:
    pass

#%%
# clean price, '$1,111' ---> '1111
def cleanNum(money): 
    money = money.strip()
    if money[0] == '$':
        money = money[1:]
    money = ''.join(money.split(','))
    return money

#%%
# get all the name of html files
fileNames = os.listdir('housesPages')

houses = []

fileWriter = open(outFolder + '/extractData.txt', 'w')

n = 0

while n < len(fileNames):  
    
    n += 1
    
    print "Processing House : ", str(n)
    
    # open a connection to each file
    with open('housesPages\Property-{}.html'.format(n)) as fileReader:
        
        # create a house dictionary to save features        
        house = {} 
        
        html = fileReader.read() 
        
        # get the address of each house, #text
        title = re.search('<title>(.*?) -', html).group(1)
        house['Address'] = title
        
        # get the zipcode, #4-digit numbers,categorical
        match = re.search('<span class="text-base" itemprop="postalCode">([\d]{5})</span>', html)
        postalCode = None
        if match:
            postalCode = match.group(1)
        house['PostalCode'] = postalCode
        
        # get the status, #text, categorical
        status = re.search('Status</span> <span>(.*?)</', html)
        if status:
            house['Status'] = status.group(1)
        
        # get the price, #number
        price = re.search('<meta itemprop="description" content="Home for Sale \|.*? \$(\S*)', html)
        if match:
            price = match.group(1)
            house['Price'] = cleanNum(price)
        house['Price'] = None
        #print house['Price']

        # obtain the source code of the table near the picture        
        segmentsTab = html.split('<meta itemprop="description" content="Home for Sale')[1].split('</div>')[0]
        
        # get all the items listed near the picture, #(key, items)         
        tab = re.findall('<li class="list-sidebyside"><span>(.+?)</span> <span>(.+?)</span>', segmentsTab)        
        house.update(dict(tab))  # append/update a dictionary
        if 'Community' in house.keys():
            house['Community'] = re.search('.*?>(.*?)</a>', house['Community']).group(1)
        
        # extract information contained in <h2> </h2>
        segmentsH2 = html.split('<h2 class="title-section title-section-detail">')
        
        for i in range(1, len(segmentsH2)-1):   # discard the first and last segments
        
            # get the h2 title
            headH2 = re.search('(.*?)</h2>', segmentsH2[i]).group(1).strip()
            if '<span' in headH2:
                headH2 = headH2.split('<span')[0].strip()
            #print headH2    
                        
            if headH2 == 'Property Details':
                
                # get the property details, #text
                match = re.search('<p class="property-description">(.*?)</p>', segmentsH2[i], re.DOTALL)
                if match:
                    propertyDetails = match.group(1).strip()
                    house['propertyDetails'] = propertyDetails
                else:
                    house['propertyDetails'] = ''
                    #print house['propertyDetails']
                
                #################################################################################                
                # split the Property Details block, regarding to <h3> 
                segmentsH3 = segmentsH2[i].split('<h3 class="title-section title-section-sub">')
                
                contentsH3 = {}
                for i in range(1,len(segmentsH3)): # discard segmentsH3[0]
                    headH3 = re.search('(.+?)</h3>', segmentsH3[i]).group(1).strip()
                    
                    if headH3 == 'General Information':    
                        generalInfo = re.findall('<li class="list-sidebyside"><span>(.*)</span><span>(.*?)</span>', segmentsH3[i])
                        if '<a href=' in generalInfo[-1][-1]:
                            typeLs = re.findall('<a.*?>(.*)</a>', generalInfo[-1][-1])
                            generalInfo[-1] = (generalInfo[-1][0], typeLs[0])
                        house.update(dict(generalInfo))  # append them into house

                    elif headH3 == 'Additional Details':
                        brokeredby = re.search('Listing Brokered by.*?<li>(.*?)</li>', segmentsH3[i], re.S)
                        if brokeredby != None:
                            brokeredby = brokeredby.group(1)
                            house['Brokeredby'] = brokeredby
                        addDetails = re.findall('<th class="span-i">\n\s+(.*?)\n.*?</th>.*?<td>(\S+)', segmentsH3[i], re.S)                                       
                        house.update(dict(addDetails)) # append them into house
                        match = re.search('<th class="span-i">.*?(Listing Agent).*?</th>\n\s+<td>\n\s+<p class="">\n\s+(.*?)</p>.*?<div id="aboutBlockR" class="hide">', segmentsH3[i],re.S)
                        match2 = re.search('<th class="span-i">.*?(Listing Agent).*?</th>\n\s+<td>\n\s+.*?<p class="nar-realtor-rep">.*?id="agentNameLnk">(.*?)</a>', segmentsH3[i],re.S)
                        listingAgent = {}
                        if match:
                            listingAgent = dict([match.groups()])
                        if match2:
                            listingAgent = dict([match2.groups()])
                        listingAgent['Listing Agent'] = listingAgent['Listing Agent'].strip()
                        house.update(listingAgent)
                        #print house['Listing Agent']

                    elif headH3 == 'Bathrooms' or 'Bathrooms' or 'Kitchen and Dining' or\
                                    'Other rooms' or 'Interior Features' or 'Building and Construction' or \
                                    'Exterior and Lot Features' or 'Garage and Parking' or \
                                    'Heating and Cooling' or 'Utilities' or 'Amenities and Community Features' or\
                                    'Homeowners Association' or 'Other Property Info' or 'Condo Info':
                        contentH3x = re.findall('<li class="">(.*?)</li>', segmentsH3[i], re.M)
                        house[headH3] = contentH3x                        
                        #print headH3, house[headH3]                      
                    else:
                        print (headH3 +'\n' +'There is a new headH3 in %d-html. Please add it into the script!' % n)
                #################################################################################3

            elif headH2 == 'On Site':
                onSite = re.findall('<tr>.*?<th class="span-i">(.*?)</th>.*?<td>(.*?)</td>.*?</tr>', segmentsH2[i], re.DOTALL)
                house.update(dict(onSite))
                #print onSite
                 
            elif 'Homes Near' in headH2:
                ## Address(text), Status(1 = 'For Sale', 0 = 'Not For Sale', None = Others), Price(num, None), Beds(num), Baths(num), Sq Ft(num)
                homesNearTemp = re.findall('<td>.*?for (.*?)">.*?<td.*?>(.*?)</td>.*?>(.*?)</td>.*?>(.*?)</td>.*?>(.*?)</td>.*?>(.*?)</td>', segmentsH2[i], re.S)
                
                #used to clean homesNearTemp
                homesNear = []   
                for row in homesNearTemp:
                    row = list(row)
                    if row[1] == 'Not For Sale':
                        row[1] = 0
                    elif row[1] == 'For Sale':
                        row[1] = 1
                    else:
                        row[1] = None
                    if row[2] == '-':
                        row[2] = None
                    else: 
                        row[2] = cleanNum(row[2])
                    if row[3] == '-':
                        row[3] = None
                    if row[4] == '-':
                        row[4] = None
                    if row[5] == '-':
                        row[5] = None
                    else:
                        row[5] = cleanNum(row[5])
                    homesNear.append(row)
                house['homesNear'] = homesNear
                #print house['homesNear']
                                            
            elif headH2 == 'Assigned Public Schools':
                assignedPSchTemp = re.findall('<a.*?>(.*?)</a>.*?>(.*?)</span></td>.*?<td>(.*?) mi</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td><i class="igs-(.*?)">', segmentsH2[i], re.S)                
                
                #%%
                # School Name(text), County Public Schools(text), Distance(num, unit:mi), Grades(text, a-b), Student/Teacher Ration(num), GreatSchools Rating(int, None))
                assignedPSch = []
                for row in assignedPSchTemp:
                    row = list(row)
                    
                    row[4] = row[4].split(':')[0]
                    if row[5] == 'p-NA':
                        row[5] = None
                    assignedPSch.append(row)
                house['assignedPSch'] = assignedPSch
                #print house['assignedPSch']
            
            #%%           
            elif headH2 == 'Nearby Schools':
                nearbySchTemp = {}
                segmentsNearbySch = segmentsH2[i].split('<div id="tab-school-')
                for i in range(1, len(segmentsNearbySch)):
                    nearbySchType = re.search('(\S+)"',segmentsNearbySch[i]).group(1) 
                    nearbySchElem = re.findall('<td>.*?>(.*?)</a>.*?</td>.*?<td>(.*?) mi</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td><i class="igs-(.*?)"', segmentsNearbySch[i], re.S)
                    nearbySchTemp[nearbySchType] = nearbySchElem                  
                
                # School Name(text), Distance(num, unit:mi, Grades(text, a-b), Student/Teacher Ration(num), GreatSchools Rating(int, None))
                nearbySch = {}
                for (key, value) in nearbySchTemp.items():
                    valueTemp = []    
                    for row in value:
                        row = list(row)
                        if row[2] == 'N/A':
                            row[2] = None
                        if row[3] == 'N/A':
                            row[3] = None
                        else:
                            row[3] = row[3].split(':')[0]
                        if row[4] == 'p-NA':
                            row[4] = None
                        valueTemp.append(row)
                    nearbySch[key] = valueTemp
                house.update(nearbySch)
                #print nearbySch
                
            # it turns out the most of this neighborhood information is (address --None), so I decide to discard it.        
            elif headH2 == 'Neighborhood Information':
                neighborhoodTemp = re.findall('<td><a.*?>(.*?)</a></td>.*?>(.*?)</td>.*?>(.*?)</td>.*?>(.*?)</td>', segmentsH2[i], re.S)

                ##Area, Average Listing Price, Price per Sq Ft, Average Sales Price
                ##however, most of the columns are None
                neighborhood = []                
                for row in neighborhoodTemp:
                    row = list(row)
                    for i in range(len(row)):
                        if row[i] == 'N/A':
                            row[i] = None
                        neighborhood.append(row)
                #print neighborhood         
                                
            elif headH2 == 'Property History':
                propertyHistTemp = re.findall('<td>(.*?)</td>.*?>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.+?)</td>.*?<td>(.*?)</td>', segmentsH2[i], re.S)
                #print propertyHistTemp

                #Date(Y-M-D), Event(Price Changed, Relisted,Listed), Price(num),  Price/Sq.Ft.(num, unit:), Change(num, percentages), Source()       
                propertyHist = []
                for row in propertyHistTemp:
                    row = list(row)
                    row[0] = str(datetime.strptime(row[0], '%m/%d/%Y').date())
                    #print datetime.strptime(row[0], '%m/%d/%Y').date()
                    if row[2] == '\xe2\x80\x94':
                        row[2] = None
                    else:
                        row[2] = cleanNum(row[2])
                    if row[3] == '\xe2\x80\x94':
                        row[3] = None
                    if row[4] == '\xe2\x80\x94':
                        row[4] = None
                    else:
                        row[4] = float(cleanNum(row[4][:-1]))*0.01
                    propertyHist.append(row)                
                house['propertyHist'] = propertyHist
                #print house['propertyHist']
                
            elif headH2 == 'Property Taxes':
                propertyTaxesTemp = re.findall('<td>(.*?)</td>.*?>(.*?)</td>.*?>(.*?)</td>.*?>.*?</td>.*?>(.*?)</td>.*?>.*?</td>.*?>(.*?)</td>', segmentsH2[i], re.S)
                #print propertyTaxesTemp
                
                #Year(num), Taxes(num, None), land(num, None),+ Additions(num, None),= Total Assessment(num, None)
                propertyTaxes = []
                for row in propertyTaxesTemp:
                    row = list(row)
                    for i in range(len(row)):
                        if row[i] == 'N/A' or row[i] == '\xe2\x80\x94' or row[i] == 'Price Unavailable':
                            row[i] = None
                        else:
                            row[i] = cleanNum(row[i])                  
                    propertyTaxes.append(row)   
                house['propertyTaxes'] = propertyTaxes
                #print house['propertyTaxes']
              
            elif headH2 == 'Location' or 'Provided by Listing Agent':
                pass  #'Location' is just a map link. 'Provided by Listing Agent' is duplicated information contained in 'Assigned Public Schools'.

            else:
                print (headH2 +'\n' +'There is a new headH2 in %d-html. Please add it into the script!' % n)
        
        houses.append(house)             
        
        fileWriter.write( str(house) +'\n' )
                   
fileWriter.close()

#%%
# it is much easier to save as a pickle file 
import pickle
f = open(outFolder + '/extractData.p', 'wb')
pickle.dump(houses, f)