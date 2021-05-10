from hrvanalysis import remove_outliers, remove_ectopic_beats, interpolate_nan_values, get_time_domain_features, get_frequency_domain_features, get_poincare_plot_features
import matplotlib.pyplot as plt
import math
import csv
import heartpy as hp
from heartpy import filter_signal
import os
import sys




def getSeizStartStopTimes(s):
  seiz1 = [14.6, 16.2]                      #seiz start and stop times in minutes - stored as global variables
  seiz2 = [62.7167, 63.7167, 175.85, 176.267]
  seiz3 = [84.567, 86.367, 154.45, 156.283]
  seiz4 = [20.167, 21.9167]
  seiz5 = [24.1167, 25.5]
  seiz6 = [51.4167, 52.3167, 124.75, 126.167]
  seiz7 = [68.033, 69.5167]
  
  if s == "01":
   return seiz1
  if s == "02":
   return seiz2
  if s == "03":
  	return seiz3
  if s == "04":
  	return seiz4
  if s == "05":
  	return seiz5
  if s == "06":
   return seiz6
  if s == "07":
  	return seiz7
   
def getNonSeizStartStopTimes(s):
   n1 = [32, 71]
   n2 = [66,118]
   n3 = [102, 175]
   n4 = [40, 63]
   n5 = [31, 70]
   n6 = [70, 105]
   n7 = [17, 42]
   
   if s == "01":
      return n1
   if s == "02":
      return n2
   if s == "03":
      return n3
   if s == "04":
      return n4
   if s == "05":
      return n5
   if s == "06":
      return n6
   if s == "07":
      return n7




#This method is only called in the removeEB method (supplement)
def getConditionedData():
  RR1 = open((subject + "RRKubios.txt"), "r")
  # rr_intervals_list contains integer values of RR-interval
  rr_intervals_list = []
  for line in RR1:
      rr_intervals_list.append(float(line[0:5]) * 1000)
  # Calculate time for original RR data
  rr_intervals_time_list = []
  for i in range(len(rr_intervals_list)):
      if i == 0:
          rr_intervals_time_list.append(rr_intervals_list[i])
      else:
          rr_intervals_time_list.append(rr_intervals_list[i] + rr_intervals_time_list[i - 1])

  # This remove outliers from signal
  rr_intervals_without_outliers = remove_outliers(rr_intervals=rr_intervals_list, low_rri=300, high_rri=2000)
  # This replace outliers nan values with linear interpolation
  interpolated_rr_intervals = interpolate_nan_values(rr_intervals=rr_intervals_without_outliers,
                                                     interpolation_method="linear")
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
          while notNANindexAfter < len(interpolated_rr_intervals) and math.isnan(
                  interpolated_rr_intervals[notNANindexAfter]):
              # Makes notNANindexAfter the index of the first non-nan nn value after index i
              notNANindexAfter += 1
          if notNANindexBefore == -1:  # If there is no non-nan RR value before index i...
              rrPlaceHolder = interpolated_rr_intervals[notNANindexAfter]
          elif notNANindexAfter == len(interpolated_rr_intervals):  # If there is no non-nan RR value after index i...
              rrPlaceHolder = interpolated_rr_intervals[notNANindexBefore]
          else:
              rrPlaceHolder = (interpolated_rr_intervals[notNANindexBefore] + interpolated_rr_intervals[
                  notNANindexAfter]) / 2
          if i == 0:
              interpolated_rr_intervals_time_list.append(rrPlaceHolder)
          else:
              interpolated_rr_intervals_time_list.append(rrPlaceHolder + interpolated_rr_intervals_time_list[i - 1])
      else:
          if i == 0:
              interpolated_rr_intervals_time_list.append(interpolated_rr_intervals[i])
          else:
              interpolated_rr_intervals_time_list.append(
                  interpolated_rr_intervals[i] + interpolated_rr_intervals_time_list[i - 1])
  for i in range(len(messedUp)):  # ADDED: Makes sure all RR Data is non-nan
      if messedUp[i] == 0:
          interpolated_rr_intervals[messedUp[i]] = interpolated_rr_intervals_time_list[messedUp[i]]
      else:
          interpolated_rr_intervals[messedUp[i]] = interpolated_rr_intervals_time_list[messedUp[i]] = \
              interpolated_rr_intervals_time_list[messedUp[i] - 1]
          
  return interpolated_rr_intervals
          
          
         
def removeEB(data, methodType):
      # This remove ectopic beats from signal
    nn_intervals_list = remove_ectopic_beats(rr_intervals=data,
                                             method=methodType)  # NN is for Normal Interval (processed RR interval data)
    # This replace ectopic beats nan values with linear interpolation
    interpolated_nn_intervals = interpolate_nan_values(rr_intervals=nn_intervals_list)

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
            elif notNANindexAfter2 == len(
                    interpolated_nn_intervals):  # If there is no non-nan NN value after index i...
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
            interpolated_nn_intervals[messedUp2[i]] = nn_intervals_time_list[messedUp2[i]] - nn_intervals_time_list[
                messedUp2[i] - 1]
                
                

    return nn_intervals_time_list, interpolated_nn_intervals
    
    
    
#This method is only called within the writeIntoExcel method (supplement)          
def getFeatures(startMin, endMin, timeData, rrData):
    dataLimitMsec = timeData[len(timeData) - 1]
    startMSec = startMin * 60 * 1000
    endMSec = endMin * 60 * 1000
    if endMSec > dataLimitMsec:
        print("End time is out of bounds! Using the end time of sample.")
        endMSec = dataLimitMsec
    startIndex = 0
    endIndex = 0
    for i in range(len(timeData)):
        if timeData[i] >= startMSec:
            startIndex = i
            break
    for i in range(len(timeData)):
        if noEB3_time[i] <= endMSec:
            endIndex = i
    listInTimeFrame = []  # Makes list of NN intervals in given time frame
    for i in range(startIndex, endIndex + 1):
        listInTimeFrame.append(rrData[i])
    # print(listInTimeFrame)
    listOfFeatures = []  # Finds features of NN intervals in given time frame
    listOfFeatures.append(
        "Min " + str(timeData[startIndex] / 1000 / 60) + " to min " + str(timeData[endIndex] / 1000 / 60) + ": ")
    listOfFeatures.append(get_time_domain_features(listInTimeFrame))
    listOfFeatures.append(get_frequency_domain_features(listInTimeFrame))
    listOfFeatures.append(get_poincare_plot_features(listInTimeFrame))
    return listOfFeatures
  


#This method creates an excel file with the data of all the features for the inputted patient number - currently only called in the getFeatureGraphs method (supplemental)
def writeIntoExcel():
  dataTimeLengthMsec = noEB3_time[len(noEB3_time)-1]    #For use later on in the method to loop through the entire file
  dataTimeLengthHr = dataTimeLengthMsec/1000/60/60
  with open(subject +"FeaturesStep " + str(step) + " " + "Window " + str(window) + ".csv", "w",
            newline='') as csvfile:
      writer = csv.writer(csvfile, delimiter=',')
      writer.writerow(header)
      startMin = 0
      if subject == "02":
         startMin = 10
            # This is the feature calculation window (the range)
      endMin = startMin + window
      
      #What each index in the list 'features' contains:
      # Index 0 is the window range
      # Index 1 is the time domain features
      # Index 2 is the frequency domain features
      # Index 3 is the poincare plot features
      
      #This block of code writes each feature into excel
      while (endMin * 60 * 1000) <= dataTimeLengthMsec:
          features = getFeatures(startMin, endMin, noEB3_time, noEB3_data)        #Use of the 'global' noEB3_time and noEB3_data variables
          index = 2  # Starting here for csv file writing
          timeDomainNumsOnly = [""] * 16  # 16 time domain elements
          timeDomainNumsOnly.insert(0,
                                    startMin)  # Columns 1 and 2 are the start and end time for feature calculation of that row
          timeDomainNumsOnly.insert(1, endMin)
          for i in range(0, len(str(features[1]))):  # loop through each character in the string
              if ((str(features[1])[i: i + 1].isdigit() and i != 0 and i != 1 and (
                      not ("_" in str(features[1])[i - 2: i]))) or str(features[1])[
                                                                   i: i + 1] == '.'):  # If the substring is a digit
                  timeDomainNumsOnly[index] += str(features[1])[
                                               i: i + 1]  # append the numbers that are not feature values (not in the header, i.e. for category 'nni_50' - the 50 will NOT be appended to this list
              elif (str(features[1])[i: i + 1] == ","):
                  index += 1
          freqDomainNumsOnly = [""] * 7  # 7 frequency domain elements
          index2 = 0
          for i in range(0, len(str(features[2]))):
              if (str(features[2])[i: i + 1].isdigit() or str(features[2])[
                                                          i: i + 1] == '.'):  # If the substring is a digit
                  freqDomainNumsOnly[index2] += str(features[2])[i: i + 1]
              elif (str(features[2])[i: i + 1] == ","):
                  index2 += 1
          poincarePlotNumsOnly = [""] * 3  # 3 poincare plot elements
          index3 = 0
          for i in range(0, len(str(features[3]))):
              if ((str(features[3])[i: i + 1].isdigit() and i != 0 and i != 1 and (
                      not ("s" in str(features[3])[i - 2: i]))) or str(features[3])[
                                                                   i: i + 1] == '.'):  # If the substring is a digit
                  poincarePlotNumsOnly[index3] += str(features[3])[i: i + 1]
              elif (str(features[3])[i: i + 1] == ","):
                  index3 += 1
          poincarePlotNumsOnly.append('')
          writer.writerow(
              timeDomainNumsOnly + freqDomainNumsOnly + poincarePlotNumsOnly)  # write the lists into the csv file
          startMin += step
          endMin += step
          
          
def normalizeList(dataToNormalize):
    minValue = dataToNormalize[0]
    for i in range(len(dataToNormalize)):
        if minValue>dataToNormalize[i]:
            minValue = dataToNormalize[i]
    maxValue = dataToNormalize[0]
    for i in range(len(dataToNormalize)):
        if maxValue<dataToNormalize[i]:
            maxValue = dataToNormalize[i]
    listRange = maxValue-minValue
    normalizedList = []
    for i in range(len(dataToNormalize)):
        normalizedList.append((dataToNormalize[i]-minValue)/listRange)
    for i in range(len(normalizedList)):
        normalizedList[i] = (normalizedList[i]*2)-1
    return normalizedList

          
          

  
  
#Gives a list of lists for the values for each feature the user requested & also a list of values for the Start Time column in the excel file
def getFeatureValues():
  writeIntoExcel()       #Create excel file
    
         #the indeces list is a list of indeces that contain the indeces in the excel file for the features the user requested
  index = 2
  indeces = []
  for i in range(len(featuresList)):
      for x in range(len(header)):
          if (featuresList[i] == header[x]):
              indeces.append(x)
              break
      if indeces == len(featuresList):
          break
          
  #values is a '2D' list that contains all the values for the features requested
  values = []
  fullData = []   #Fulldata is the entire data from the excel file as a '2D' list of strings
  fileTEST = open(subject + "FeaturesStep " + str(step) + " " + "Window " + str(window) + ".csv", "r")
  dataTEST = csv.reader(fileTEST)
  for row in dataTEST:
      fullData.append(row)
  for i in indeces:
      temp = []
      for row in fullData:
          if (not (row[i] == header[i])):
              temp.append(float(row[i]))
      values.append(temp)
  fileTEST.close()
  
  timesList = []
  with open(subject + "FeaturesStep " + str(step) + " " + "Window " + str(window) + ".csv", "r") as csvdata:
      data = csv.reader(csvdata)
      for row in data:
         if (not (row[0] == "Start Time")):
            timesList.append(float(row[0]))  # Append all Start Time vals into timesList
            

  if normalized == "yes":
    for i in range(len(values)):
      values[i] = normalizeList(values[i])
      
            
  return timesList, values


def trimFeaturesListSeizures(seizureStartTime): # Returns two 2d lists: one of values 3 min before the seizure, one of values 1 min during the seizure
  times, values = getFeatureValues()
  # Seizure start and end times are given in minutes; times is also in minutes
  seizureStartTimeIndex = 0
  for i in range(len(times)):
    if times[i]<=seizureStartTime:
      seizureStartTimeIndex=i
  seizureStopTimeIndex = seizureStartTimeIndex+4
  threeMinBeforeSeizureIndex = seizureStartTimeIndex-12 # 3 min before seizure
  # Values 3 min before seizure goes from threeMinBeforeSeizureIndex to seizureStartTimeIndex
  # Values 1 min during seizure goes from seizureStartTimeIndex to seizureStopTimeIndex
  values3minBefore = []
  values1minDuring = []
  for i in range(len(values)):
    featuresListBef = []
    featuresListDur = []
    for x in range(threeMinBeforeSeizureIndex, seizureStartTimeIndex+1):
      featuresListBef.append(values[i][x])
    for y in range(seizureStartTimeIndex, seizureStopTimeIndex+1):
      featuresListDur.append(values[i][y])
    values3minBefore.append(featuresListBef)
    values1minDuring.append(featuresListDur)
  return values3minBefore, values1minDuring  
   
def writeSeizExcelClassifierPoints():
  seiz = getSeizStartStopTimes(subject)
  nonSeiz = getNonSeizStartStopTimes(subject)
  before = []
  during = []
  if subject == "02" or subject == "03" or subject == "06":
   before, during = trimFeaturesListSeizures(seiz[0])
   
   beforePeaks = []
   duringPeaks = []
	
   for i in range(len(before)):
     peak = abs(before[i][0])
     for j in range(len(before[i])):
    	 if abs(before[i][j]) > peak:
          peak = before[i][j]
     beforePeaks.append(peak)
  
        
   for i in range(len(during)):
    peak = abs(during[i][0])
    for j in range(len(during[i])):
      if abs(during[i][j]) > peak:
        peak = during[i][j]
    duringPeaks.append(peak)
    
        
        
        
   fileAlreadyExists = os.path.isfile("Classifier Peak Points - Normalized.csv")
   if not(fileAlreadyExists):
      header2 = ['', 'mean_nni B', 'sdnn B', 'mean_hr B', 'std_hr B', 'vlf B', "mean_nni D", "sdnn D", "mean_hr D", "std_hr D", "vlf", "Seiz"]
      csvfile = open ("Classifier Peak Points - Normalized.csv", "w", newline = '')
      write = csv.writer(csvfile, delimiter = ",")
      write.writerow(header2)
   else:
     csvfile = open ("Classifier Peak Points - Normalized.csv", "a", newline = '')
     write = csv.writer(csvfile, delimiter = ",")
   temp = [subject + 'Seiz1']
   for peak in beforePeaks:
     temp.append(str(peak))

   for peak in duringPeaks:
     temp.append(str(peak))
     
   temp.append("0")
   
   write.writerow(temp)

   before, during = trimFeaturesListSeizures(seiz[2])
  else:
    before, during = trimFeaturesListSeizures(seiz[0])
  firstOrSecond = "1"
  if subject == "02" or subject == "03" or subject == "06":
   firstOrSecond = "2"
    
    
  beforePeaks = []
  duringPeaks = []
	
  for i in range(len(before)):
    peak = abs(before[i][0])
    for j in range(len(before[i])):
    	if abs(before[i][j]) > peak:
         peak = before[i][j]
    beforePeaks.append(peak)
        
  for i in range(len(during)):
   peak = abs(during[i][0])
   for j in range(len(during[i])):
     if abs(during[i][j]) > peak:
       peak = during[i][j]
   duringPeaks.append(peak)
        
        
        
  fileAlreadyExists = os.path.isfile("Classifier Peak Points - Normalized.csv")
  if not(fileAlreadyExists):
     header2 = ['', 'mean_nni B', 'sdnn B', 'mean_hr B', 'std_hr B', 'vlf B', "mean_nni D", "sdnn D", "mean_hr D", "std_hr D", "vlf D", "Seiz"]
     csvfile = open ("Classifier Peak Points - Normalized.csv", "w", newline = '')
     write = csv.writer(csvfile, delimiter = ",")
     write.writerow(header2)
  else:
    csvfile = open ("Classifier Peak Points - Normalized.csv", "a", newline = '')
    write = csv.writer(csvfile, delimiter = ",")
    
  temp = [subject + 'Seiz' + firstOrSecond]
  for peak in beforePeaks:
    temp.append(str(peak))
    
  for peak in duringPeaks:
    temp.append(str(peak))
    
  temp.append("0")
   
  write.writerow(temp)
 
    
       
    
    
def writeNonSeizExcelClassifierPoints():
  nonSeiz = getNonSeizStartStopTimes(subject)
  x = 0
  while x < 2:
     beforeNon, duringNon= trimFeaturesListSeizures(nonSeiz[x])
     nonSeizBeforePeaks = []
     nonSeizDuringPeaks = []
   	
     for i in range(len(beforeNon)):
       peak = abs(beforeNon[i][0])
       for j in range(len(beforeNon[i])):
       	if abs(beforeNon[i][j]) > peak:
            peak = beforeNon[i][j]
       nonSeizBeforePeaks.append(peak)
       
     for i in range(len(duringNon)):
       peak = abs(duringNon[i][0])
       for j in range(len(duringNon[i])):
       	if abs(duringNon[i][j]) > peak:
            peak = duringNon[i][j]
       nonSeizDuringPeaks.append(peak)
            
     fileAlreadyExists = os.path.isfile("Classifier Peak Points - Normalized.csv")
     if not(fileAlreadyExists):
        print ("You need to call the writeSeizExcelClassifierPoints method first")
        sys.exit()
     else:
       csvfile = open ("Classifier Peak Points - Normalized.csv", "a", newline = '')
       write = csv.writer(csvfile, delimiter = ",")
     
     temp = [subject + 'NS' + str(x + 1)]
     for peak in nonSeizBeforePeaks:
       temp.append(str(peak))
     
     for peak in nonSeizDuringPeaks:
       temp.append(str(peak))
       
     temp.append("1")
     
     write.writerow(temp)
     
     x += 1

      
      

    
#This method creates graphs for the indicated features inputted at the beginning by the user - REQUIRES EXCEL FILES
def getFeatureGraphs():


  if (normalized == "no"):
    question = input("Would you like a custom y min and y max for your graph(s)? Input 0 for yes, 1 for no: ")   #This block of code is for the scale
    mins = []
    maxes = []
    if question == "1":
      for x in featuresList:        #use of 'global' featuresList variable
          mins.append(-1.0)
          maxes.append(-1.0)
    else:
      for feature in featuresList:
          min = float(input(
              "What would you like the min y-value to be for " + feature + "? Enter -1 if you would like the default y - value: "))
          max = float(input(
              "What would you like the max y-value to be for " + feature + "? Enter -1 if you would like the default y - value: "))
          mins.append(min)
          maxes.append(max)

  print ("hello")
  timesList, values = getFeatureValues() #Call the getFeatureValues method
  print ("hello")
  indexVal = 0
  for i in range(len(featuresList)):  # For each feature requested
    plt.figure("Patient" + subject + " - " + (featuresList[indexVal]))
    plt.plot(timesList, values[indexVal])  # Plot graph
    if subject == "01":  # Depending on which subject was requested, plot vertical lines where that subject's seizure starts and stops
      for z in range(len(seiz1)):
         plt.axvline(x=seiz1[z], color='r')
    if subject == "02":
      for z in range(len(seiz2)):
        plt.axvline(x=seiz2[z], color='r')
    if subject == "03":
      for z in range(len(seiz3)):
         plt.axvline(x=seiz3[z], color='r')
    if subject == "04":
      for z in range(len(seiz4)):
         plt.axvline(x=seiz4[z], color='r')
    if subject == "05":       
      for z in range(len(seiz5)):
        plt.axvline(x=seiz5[z], color='r')
    if subject == "06":
      for z in range(len(seiz6)):
        plt.axvline(x=seiz6[z], color='r')
    if subject == "07":
      for z in range(len(seiz7)):
        plt.axvline(x=seiz7[z], color='r')
    plt.xlabel("time (min)")
    plt.ylabel(featuresList[indexVal])
    plt.xlim(0, timesList[-1])
    

    
    if normalized == "no":
      ymin = mins[indexVal]
      ymax = maxes[indexVal]
      if ((not (ymin == -1.0)) or (not (ymax == -1.0))):
        plt.ylim(ymin, ymax)
    else:
      plt.ylim(0, 1)
      
    
    plt.title("sz" + str(subject) + " - " + (featuresList[indexVal]))
    plt.show()  # Show the graph
    indexVal += 1

                  
                  
def createKubiosFile():                                                                               #NEW FUNCTION 2
   MyFile = open("Patient" + subject + "PROCESSED.txt", "w") #This block of code writes the processed data into text files that can be read into Kubios
   for i in range(len(noEB3_data)):                                        #This method uses the 'global' variables noEB3_time & noEB3_data
      MyFile.write(str(noEB3_data[i]) + "\t" + str(noEB3_time[i]) + "\n")
    




subject = input("Whose data do you want to look at? ")
normalized = input("Do you want your data to be normalized? Enter yes or no: ")
step = 0.25
window = 3.0
header = ["Start Time", "End Time", "mean_nni", "sdnn", "sdsd", "nni_50", "pnni_50", "nni_20", "pnni_20", "rmssd",
          "median_nni", "range_nni", "cvsd", "cvnni", "mean_hr", "max_hr", "min_hr", "std_hr", "lf", "hf",
          "lf_hf_ratio", "lfnu", "hfnu", "total_power", "vlf", "sd1", "sd2", "ratio_sd2_sd1", '']


#The purpose of this block of code is to gather the features the user wants to look into
all = header[2: 28]
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
        print("Feature not found")
 

##These are the global variables that are used in multiple methods at the bottom of the program (represent processed rr data)
interpolated_rr_intervals = getConditionedData()
noEB1_time, noEB1_data = removeEB(interpolated_rr_intervals, "karlsson")
noEB2_time, noEB2_data = removeEB(noEB1_data, "kamath")
noEB3_time, noEB3_data = removeEB(noEB2_data, "malik") # The conditioned data will be in noEB3_data and the corresponding times will be in noEB3_time.


sample_rate = float(input("What do you want the sample rate to be? "))

noEB3_data = hp.remove_baseline_wander(noEB3_data, sample_rate, cutoff=0.05) #TESTING HEARTPY - MIDDLE VALUE IS THE SAMPLE_RATE


writeSeizExcelClassifierPoints()
writeNonSeizExcelClassifierPoints()



#getFeatureGraphs()         #Display Graphs
