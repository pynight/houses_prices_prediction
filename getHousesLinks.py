import urllib2
#import time

browser=urllib2.build_opener()

browser.addheaders=[('User-agent', 'Mozilla/5.0')]

pagesToGet=104  #total pages for scraping

#create a new file, which we will use to store the links of houses listed at Http://www.realtor.com.
fileWriter=open('housesLinks.txt','wb')

#for every number in the range from 1 to pageNum+1  
for page in range(1,pagesToGet+1):
    
    print 'processing page :', page
    
    #time.sleep(randint(60))
    
    url='http://www.realtor.com/realestateandhomes-search/Silver-Spring_MD/sby-1/pg-' + str(page)
    
    response=browser.open(url)    
    
    myHTML=response.read()
        
    segments=myHTML.split('class="ellipsis" href="') # split into 11 segements
    
    #for all the segments except the 1st one
    for j in range(1,len(segments)):
        
        #get the segment in the j-th position
        segment=segments[j]
        
        #find the position of the first double quote character "  in the segment
        index=segment.find('"')
                
        #get the part (sub-string) of the segment from position 0 all the way to (but excluding) position index
        link= segment[0:index]
                
        #write the link to the hourses' profile to the file. One link per line, so '\n' character is added.
        fileWriter.write('http://www.realtor.com'+link+'\n')

fileWriter.close()