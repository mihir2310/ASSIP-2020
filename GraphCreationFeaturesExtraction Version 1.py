from hrvanalysis import remove_outliers, remove_ectopic_beats, interpolate_nan_values, get_time_domain_features, get_frequency_domain_features, get_poincare_plot_features
import matplotlib.pyplot as plt
import math
import csv

subject = input("Whose data do you want to look at? ")
step = float(input("Step value - How often should the HRV be taken (in minutes)? "))     #step and window are for use later on when csv file writing
window = float(input("Window range value - How much time should it take to measure the hrv each time (in minutes)? "))
header = ["Start Time", "End Time", "mean_nni", "sdnn", "sdsd", "nni_50", "pnni_50", "nni_20", "pnni_20", "rmssd", "median_nni", "range_nni", "cvsd", "cvnni", "mean_hr", "max_hr", "min_hr", "std_hr", "lf", "hf", "lf_hf_ratio", "lfnu", "hfnu", "total_power", "vlf", "sd1", "sd2", "ratio_sd2_sd1", '']
all = header[2 : 28]
cont = bool(True)
featuresList = []
while (cont):
   features = input("Enter the features you would like - \"all\" to select all features - 0 to stop: ")
   if features == "all":
      for i in range(len(all)):
         featuresList.append(all[i])
      cont = bool(False)
   elif (features in header):
      featuresList.append(features)
   elif features == "0":
      cont = bool(False)
   else:
      print ("Feature not found") 
      
question = input("Would you like a custom y min and y max for your graph(s)? Input 0 for yes, 1 for no: ")
mins = []
maxes = []
if question == "1":
   for x in featuresList:
      mins.append(-1.0)
      maxes.append(-1.0)
else:
   for feature in featuresList:
      min = float(input("What would you like the min y-value to be for " + feature + "? Enter -1 if you would like the default y - value: "))
      max = float(input("What would you like the max y-value to be for " + feature + "? Enter -1 if you would like the default y - value: "))
      mins.append(min)
      maxes.append(max)

seiz1 = [14.6, 16.2]        #seiz start and stop times
seiz2 = [62.7167, 63.7167, 175.85, 176.267]
seiz3 = [84.567, 86.367, 154.45, 156.283]
seiz4 = [20.167, 21.9167]
seiz5 = [24.1167, 25.5]
seiz6 = [51.4167, 52.3167, 124.75, 126.167]
seiz7 = [68.033, 69.5167]
   
RR1 = open((subject+"RRKubios.txt"), "r")
# rr_intervals_list contains integer values of RR-interval
rr_intervals_list = []
for line in RR1:
   rr_intervals_list.append(float(line[0:5])*1000)
print("Here is the raw rr data read in milliseconds: ")
print(rr_intervals_list)
# Calculated time for original RR data
rr_intervals_time_list = []
for i in range(len(rr_intervals_list)):
   if i==0:
      rr_intervals_time_list.append(rr_intervals_list[i])
   else:
      rr_intervals_time_list.append(rr_intervals_list[i]+rr_intervals_time_list[i-1])
print("Here are the times for the raw rr data read in milliseconds: ")
print(rr_intervals_time_list)
print("\n")

# This remove outliers from signal
rr_intervals_without_outliers = remove_outliers(rr_intervals=rr_intervals_list, low_rri=300, high_rri=2000)
# This replace outliers nan values with linear interpolation
interpolated_rr_intervals = interpolate_nan_values(rr_intervals=rr_intervals_without_outliers,interpolation_method="linear")
print("Here is the rr data without outliers in milliseconds: ")
#for i in range(len(interpolated_rr_intervals)):
#   print(str(i)+": "+str(interpolated_rr_intervals[i]))
print(interpolated_rr_intervals)
# Calculated time for RR data without outliers
messedUp = []
interpolated_rr_intervals_time_list = []
for i in range(len(interpolated_rr_intervals)):
   # If the interpolated rr value is nan, 0 is used as placeholder
   if math.isnan(interpolated_rr_intervals[i]):
      messedUp.append(i)
      # NEW CHANGE: Instead of using 0 as a placeholder, find the average of the previous and after rr values or the closest rr value and use it as a placeholder
      notNANindexBefore = i - 1
      notNANindexAfter = i + 1
      while notNANindexBefore > -1 and math.isnan(interpolated_rr_intervals[notNANindexBefore]):
         # Makes notNANindexBefore the index of the first non-nan rr value before index i
         notNANindexBefore -= 1
      while notNANindexAfter < len(interpolated_rr_intervals) and math.isnan(interpolated_rr_intervals[notNANindexAfter]):
         # Makes notNANindexAfter the index of the first non-nan nn value after index i
         notNANindexAfter += 1
      if notNANindexBefore == -1:  # If there is no non-nan RR value before index i...
         rrPlaceHolder = interpolated_rr_intervals[notNANindexAfter]
      elif notNANindexAfter == len(interpolated_rr_intervals):  # If there is no non-nan RR value after index i...
         rrPlaceHolder = interpolated_rr_intervals[notNANindexBefore]
      else:
         rrPlaceHolder = (interpolated_rr_intervals[notNANindexBefore] + interpolated_rr_intervals[notNANindexAfter])/2
      if i == 0:
         interpolated_rr_intervals_time_list.append(rrPlaceHolder)
      else:
         interpolated_rr_intervals_time_list.append(rrPlaceHolder + interpolated_rr_intervals_time_list[i - 1])
   else:
      if i==0:
         interpolated_rr_intervals_time_list.append(interpolated_rr_intervals[i])
      else:
         interpolated_rr_intervals_time_list.append(interpolated_rr_intervals[i]+interpolated_rr_intervals_time_list[i-1])
for i in range(len(messedUp)): # ADDED: Makes sure all RR Data is non-nan
   if messedUp[i]==0:
      interpolated_rr_intervals[messedUp[i]]=interpolated_rr_intervals_time_list[messedUp[i]]
   else:
      interpolated_rr_intervals[messedUp[i]]=interpolated_rr_intervals_time_list[messedUp[i]]=interpolated_rr_intervals_time_list[messedUp[i]-1]

print("Here are the times for the rr data without outliers read in milliseconds: ")
#for i in range(len(interpolated_rr_intervals_time_list)):
#   print(str(i)+": "+str(interpolated_rr_intervals_time_list[i]))
print(interpolated_rr_intervals_time_list)
print("Data at these indices was nan: "+str(messedUp))
print("\n")

def removeEB(data, methodType):
   # This remove ectopic beats from signal
   nn_intervals_list = remove_ectopic_beats(rr_intervals=data, method=methodType)  # NN is for Normal Interval (processed RR interval data)
   # This replace ectopic beats nan values with linear interpolation
   interpolated_nn_intervals = interpolate_nan_values(rr_intervals=nn_intervals_list)
   print("Here is the nn data read in milliseconds: ")
   # for i in range(len(interpolated_nn_intervals)):
   #   print(str(i)+": "+str(interpolated_nn_intervals[i]))
   print(interpolated_nn_intervals)
   # Calculated time for RR data without ectopic beats
   messedUp2 = []
   nn_intervals_time_list = []
   for i in range(len(interpolated_nn_intervals)):
      # If the interpolated nn value is nan, 0 is used as placeholder
      if math.isnan(interpolated_nn_intervals[i]):
         messedUp2.append(i)
         # NEW CHANGE: Instead of using 0 as a placeholder, find the average of the previous and after NN values or the closest NN value and use it as a placeholder
         notNANindexBefore2 = i - 1
         notNANindexAfter2 = i + 1
         while notNANindexBefore2 > -1 and math.isnan(interpolated_nn_intervals[notNANindexBefore2]):
            # Makes notNANindexBefore2 the index of the first non-nan nn value before index i
            notNANindexBefore2 -= 1
         while notNANindexAfter2 < len(interpolated_nn_intervals) and math.isnan(
                 interpolated_nn_intervals[notNANindexAfter2]):
            # Makes notNANindexAfter2 the index of the first non-nan nn value after index i
            notNANindexAfter2 += 1
         if notNANindexBefore2 == -1:  # If there is no non-nan NN value before index i...
            nnPlaceHolder = interpolated_nn_intervals[notNANindexAfter2]
         elif notNANindexAfter2 == len(interpolated_nn_intervals):  # If there is no non-nan NN value after index i...
            nnPlaceHolder = interpolated_nn_intervals[notNANindexBefore2]
         else:
            nnPlaceHolder = (interpolated_nn_intervals[notNANindexBefore2] + interpolated_nn_intervals[
               notNANindexAfter2]) / 2
         if i == 0:
            nn_intervals_time_list.append(nnPlaceHolder)
         else:
            nn_intervals_time_list.append(nnPlaceHolder + nn_intervals_time_list[i - 1])
      else:
         if i == 0:
            nn_intervals_time_list.append(interpolated_nn_intervals[i])
         else:
            nn_intervals_time_list.append(interpolated_nn_intervals[i] + nn_intervals_time_list[i - 1])
   for i in range(len(messedUp2)):  # ADDED: Makes sure all RR Data is non-nan
      if messedUp2[i] == 0:
         interpolated_nn_intervals[messedUp2[i]] = nn_intervals_time_list[messedUp2[i]]
      else:
         interpolated_nn_intervals[messedUp2[i]] = nn_intervals_time_list[messedUp2[i]] - nn_intervals_time_list[messedUp2[i]-1]
   """
   print("Here are the times for the nn data read in milliseconds: ")
   # for i in range(len(nn_intervals_time_list)):
   #   print(str(i)+": "+str(nn_intervals_time_list[i]))
   print(nn_intervals_time_list)
   print("Data at these indices was nan: " + str(messedUp2))
   print("\n")
   """
   return nn_intervals_time_list, interpolated_nn_intervals

noEB1_time, noEB1_data = removeEB(interpolated_rr_intervals, "karlsson")
noEB2_time, noEB2_data = removeEB(noEB1_data, "kamath")
noEB3_time, noEB3_data = removeEB(noEB2_data, "malik") # The conditioned data will be in noEB3_data and the corresponding times will be in noEB3_time.

print("Here are the times for the nn data read in milliseconds: ")
print(noEB3_time)
print("\n")

dataTimeLengthMsec = noEB3_time[len(noEB3_time)-1]
dataTimeLengthHr = dataTimeLengthMsec/1000/60/60
print("The sample is " + str(dataTimeLengthHr) + " hrs long.\n")

def getFeatures(startMin, endMin, timeData, rrData):
   dataLimitMsec = timeData[len(timeData)-1]
   startMSec = startMin*60*1000
   endMSec = endMin*60*1000
   if endMSec>dataLimitMsec:
      print("End time is out of bounds! Using the end time of sample.")
      endMSec = dataLimitMsec
   startIndex = 0
   endIndex = 0
   for i in range(len(timeData)):
      if timeData[i]>=startMSec:
         startIndex=i
         break
   for i in range(len(timeData)):
      if noEB3_time[i]<=endMSec:
         endIndex = i
   listInTimeFrame = [] # Makes list of NN intervals in given time frame
   for i in range(startIndex, endIndex+1):
      listInTimeFrame.append(rrData[i])
   #print(listInTimeFrame)
   listOfFeatures = [] # Finds features of NN intervals in given time frame
   listOfFeatures.append("Min " + str(timeData[startIndex]/1000/60) + " to min " + str(timeData[endIndex]/1000/60) + ": ")
   listOfFeatures.append(get_time_domain_features(listInTimeFrame))
   listOfFeatures.append(get_frequency_domain_features(listInTimeFrame))
   listOfFeatures.append(get_poincare_plot_features(listInTimeFrame))
   return listOfFeatures

with open(subject + "FeaturesStep " + str(step) + " " + "Window " + str(window) + ".csv", "w", newline = '') as csvfile:  #Open or create a new csv file for the features to be written into for each time window
   writer = csv.writer(csvfile, delimiter = ',')
   writer.writerow(header)
   startMin = 0              #This is the feature calculation window (the range)
   endMin = startMin + window
#Index 0 is the window range
#Index 1 is the time domain features
#Index 2 is the frequency domain features
#Index 3 is the poincare plot features
   while (endMin*60*1000)<=dataTimeLengthMsec:
      features = getFeatures(startMin, endMin, noEB3_time, noEB3_data)
      index = 2       #Starting here for csv file writing
      timeDomainNumsOnly = [""] * 16 #16 time domain elements
      timeDomainNumsOnly.insert(0, startMin)  #Columns 1 and 2 are the start and end time for feature calculation of that row
      timeDomainNumsOnly.insert(1, endMin)
      for i in range (0, len(str(features[1]))):     #loop through each character in the string
         if ((str(features[1])[i : i + 1].isdigit() and i != 0 and i != 1 and (not("_" in str(features[1])[i - 2 : i]))) or str(features[1])[i : i + 1] == '.'):   #If the substring is a digit
            timeDomainNumsOnly[index] += str(features[1])[i : i + 1]  #append the numbers that are not feature values (not in the header, i.e. for category 'nni_50' - the 50 will NOT be appended to this list
         elif (str(features[1])[i : i + 1] == ","):
            index += 1
      freqDomainNumsOnly = [""] * 7 #7 frequency domain elements
      index2 = 0
      for i in range (0, len(str(features[2]))):
         if (str(features[2])[i : i + 1].isdigit() or str(features[2])[i : i + 1] == '.'):   #If the substring is a digit
            freqDomainNumsOnly[index2] += str(features[2])[i : i + 1]
         elif (str(features[2])[i : i + 1] == ","):
            index2 += 1
      poincarePlotNumsOnly = [""] * 3 #3 poincare plot elements
      index3 = 0
      for i in range (0, len(str(features[3]))):
         if ((str(features[3])[i : i + 1].isdigit() and i != 0 and i != 1 and (not("s" in str(features[3])[i - 2: i]))) or str(features[3])[i : i + 1] == '.'):   #If the substring is a digit
            poincarePlotNumsOnly[index3] += str(features[3])[i : i + 1]
         elif (str(features[3])[i : i + 1] == ","):
            index3 += 1
      poincarePlotNumsOnly.append('')
      writer.writerow(timeDomainNumsOnly + freqDomainNumsOnly + poincarePlotNumsOnly)   #write the lists into the csv file
      startMin += step
      endMin += step

#This block of code is for converting the processed data into files that can be read into Kubios
#MyFile = open("Patient" + subject + "PROCESSED.txt", "w") #This block of code writes the processed data into text files that can be read into Kubios
#for i in range(len(noEB3_data)):
#   MyFile.write(str(noEB3_data[i]) + "\t" + str(noEB3_time[i]) + "\n")

#feature graphs
index = 2
indeces = []
for i in range(len(featuresList)):
   for x in range(len(header)):
      if (featuresList[i] == header[x]):
         indeces.append(x)
         break
   if indeces == len(featuresList):
      break
values = []
fullData = []
fileTEST = open(subject + "FeaturesStep " + str(step) + " " + "Window " + str(window) + ".csv", "r")
dataTEST = csv.reader(fileTEST)
for row in dataTEST:
   fullData.append(row)
for i in indeces:
   temp = []
   for row in fullData:
      if (not(row[i] == header[i])):
         temp.append(float(row[i]))
   values.append(temp)
fileTEST.close()
         
      
with open(subject + "FeaturesStep " + str(step) + " " + "Window " + str(window) + ".csv", "r") as csvdata:
   data = csv.reader(csvdata)
   indexVal = 0
   for row in data:    #For loop only for header access
      timesList = []
      if (row[0] == "Start Time"):
         for row1 in data:
            if (not(row1[0] == "Start Time")):
               timesList.append(float(row1[0]))      #Append all Start Time vals into timesList  
         for i in indeces:                    #For each feature requested
            plt.figure("Patient" + subject + " - " + (header[i]))
            plt.plot(timesList, values[indexVal])     #Plot graph
            if subject == "01":                 #Depending on which subject was requested, plot vertical lines where that subject's seizure starts and stops
               for z in range(len(seiz1)):
                  plt.axvline(x = seiz1[z], color = 'r')
            if subject == "02":
               for z in range(len(seiz2)):
                  plt.axvline(x = seiz2[z], color = 'r')
            if subject == "03":
               for z in range(len(seiz3)):
                  plt.axvline(x = seiz3[z], color = 'r')
            if subject == "04":
               for z in range(len(seiz4)):
                  plt.axvline(x = seiz4[z], color = 'r')
            if subject == "05":
               for z in range(len(seiz5)):
                  plt.axvline(x = seiz5[z], color = 'r')
            if subject == "06":
               for z in range(len(seiz6)):
                  plt.axvline(x = seiz6[z], color = 'r')
            if subject == "07":
               for z in range(len(seiz7)):
                  plt.axvline(x = seiz7[z], color = 'r')
            plt.xlabel("time (min)")
            plt.ylabel(header[i])
            plt.xlim(0, timesList[-1])
            ymin = mins[indexVal]
            ymax = maxes[indexVal]
            if ((not(ymin == -1.0)) or (not(ymax == -1.0))):
               plt.ylim(ymin, ymax)
            plt.title("sz" + str(subject) + " - " + (header[i]))
            plt.show()       #Show the graph
            indexVal += 1
      
      
# This part is for making the graphs using matplotlib - I commented it out because we are doing feature calculations now





"""
plt.figure("Sub"+subject+"OG")
plt.plot(rr_intervals_time_list, rr_intervals_list, 'r')
plt.xlabel("Time (ms)")
#plt.xlim(0,5400)
plt.ylabel("RR (ms)")
plt.title("Subject" + str(subject)+" original RR data")

plt.figure("Sub"+subject+"woOutliers")
plt.plot(interpolated_rr_intervals_time_list, interpolated_rr_intervals, 'g')
plt.xlabel("Time (ms)")
plt.ylabel("RR (ms)")
plt.title("Subject" + str(subject)+" RR data without outliers")

plt.figure("Sub"+subject+"woEB2")
plt.plot(noEB3_time, noEB3_data, 'b') # Changed to interpolated nn list
plt.xlabel("Time (ms)")
plt.ylabel("RR (ms)")
plt.title("Subject" + str(subject)+" RR data wo EB using all removal methods but acar")
plt.show()
"""
