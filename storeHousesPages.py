import urllib2, os
#import time

browser=urllib2.build_opener()

browser.addheaders=[('User-agent', 'Mozilla/5.0')]

# this is the name of the folder which is used to store the profile pages of housese
outFolder='housesPages'

# if the folder doesn't exist, make it 
if not os.path.exists(outFolder): 
    os.mkdir(outFolder) 

fileReader=open('housesLinks.txt', 'r')

count = 1  # use to restart download, if it is forced closed by the server.

# read houseseLinks line by line
for line in fileReader:   
    
    link=line.strip()
    
    #time.sleep(5)
    
    if count >= 1:  # change the number to the last number that has been downloaded
        
        print 'Donwloading: {} ||'.format(count), link
        
        html=browser.open(link).read()
    
        #name=link[link.rfind('/')+1:]
        
        fileWriter=open(outFolder+'/Property-'+str(count)+'.html', 'w')

        fileWriter.write(html)

        fileWriter.close()

    count += 1

fileReader.close()