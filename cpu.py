loc = ["AWS", "GCP", "AZURE"] #list of clouds (list is a data structure that holds multiple values of different types)
# array is a data structure tha holds multiple values but of same type
cloud = "GCP" 
# add a new cloud
loc.insert(1, "alibaba")
loc.insert(0, "Oracle") # typo in append, should be append
loc.append("IBM") # append adds a new value to the end of the list
for cloud in loc: # for loop iterates over the list
    print (" ")
    print (cloud) # prints each cloud in the list
for i in range (1,10-1):  # for loop iterates over a range of numbers
    print (i) # prints each number in the range
