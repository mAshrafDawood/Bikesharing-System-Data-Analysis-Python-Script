import time
import threading
import pandas as pd
import numpy as np
from queue import Queue


# Getting Filters from user
def getFirstFilter():
    gotFilter = False
    while not gotFilter:
        print("How would you like to filter the data ? (Please use only numbers from 1 to 4)")
        try:
            firstFilter = int(input("1.Month\n2.Day\n3.Month and Day\n4.No Filters\n->"))
            gotFilter = True
        except ValueError:
            gotFilter = False
            continue
        if firstFilter == 1:
            return None, getMonthFilter(), cityOfChoice()
        elif firstFilter == 2:
            return getDayFilter(), None, cityOfChoice()
        elif firstFilter == 3:
            return getDayFilter(), getMonthFilter(), cityOfChoice()
        elif firstFilter == 4:
            return None, None, cityOfChoice()
        else:
            gotFilter = False


# Getting Month Filter
def getMonthFilter():
    gotFilter = False
    while not gotFilter:
        print("Choose a month (Please use numbers only)")
        try:
            monthFilter = int(input("1.January\n2.February\n3.March\n4.April\n5.May\n6.June\n7.July\n->"))
            gotFilter = True
            if monthFilter > 7 or monthFilter < 1:
                gotFilter = False
        except ValueError:
            gotFilter = False

    return monthFilter


# Getting Day Filter
def getDayFilter():
    gotFilter = False
    while not gotFilter:
        try:
            dayFilter = int(input("Choose a day (Please use numbers from 1 to 7)\n->"))
            gotFilter = True
            if dayFilter > 7 or dayFilter < 1:
                gotFilter = False
        except ValueError:
            gotFilter = False

    return numToDay(dayFilter)


# Converting numbers to day name
def numToDay(num):
    if num == 1:
        return "Sunday"
    elif num == 2:
        return "Monday"
    elif num == 3:
        return "Tuesday"
    elif num == 4:
        return "Wednesday"
    elif num == 5:
        return "Thursday"
    elif num == 6:
        return "Friday"
    else:
        return "Saturday"


# Choosing a city
def cityOfChoice():
    gotCity = False
    while not gotCity:
        print("Choose a city to apply these filters on (Kindly use numbers only)")
        try:
            city = int(input("1.Chicago\n2.New York\n3.Washignton\n->"))
            gotCity = True
            if city > 3 or city < 1:
                gotCity = False
        except ValueError:
            gotCity = False
    if city == 1:
        return "Chicago"
    elif city == 2:
        return "New York City"
    elif city == 3:

        return "Washington"


if __name__ == '__main__':
    start = True
    while start:
        print("Hello! Ready to explose some US Bikeshare data ?")
        que = Queue()
        filterThread = threading.Thread(target=lambda dum, arg1: dum.put(getFirstFilter()), args=(que, 0))
        filterThread.start()

        # Reading Data
        myDataBase = {
            'Chicago': pd.read_csv("chicago.csv"),
            'New York City': pd.read_csv("new_york_city.csv"),
            'Washington': pd.read_csv("washington.csv")
        }

        # Correcting datatypes
        for key in myDataBase.keys():
            myDataBase[key]['Start Time'] = pd.to_datetime(myDataBase[key]['Start Time'], dayfirst=True)
            myDataBase[key]['End Time'] = pd.to_datetime(myDataBase[key]['End Time'], dayfirst=True)

        # Waiting for filters
        while filterThread.is_alive():
            time.sleep(0.01)
        filterThread.join()
        myFilters = que.get()

        numAppliedFilters = 1
        # 0 for Day Filter
        # 1 for Month Filter
        # 2 for city
        print("Filters Are set to:")
        print("\tDay:", myFilters[0])
        print("\tMonth:", myFilters[1])
        print("\tCity:", myFilters[2])
        print("Filtering your data ....")
        t0 = time.time()  # Start Time
        dataToApply = myDataBase[myFilters[2]]
        dataToApply['Start Day Name'] = dataToApply['Start Time'].dt.day_name()
        dataToApply['End Day Name'] = dataToApply['End Time'].dt.day_name()
        if (myFilters[0] is not None) and (myFilters[1] is not None):  # Applying Day&Month Filter
            numAppliedFilters += 2
            dataAfterFilter = dataToApply.loc[dataToApply['Start Day Name'] == myFilters[0]]
            dataAfterFilter = dataAfterFilter.loc[dataAfterFilter['Start Time'].dt.month == myFilters[1]]
            dataAfterFilter.append(dataToApply.loc[dataToApply['End Day Name'] == myFilters[0]])
            dataAfterFilter = dataAfterFilter.loc[dataAfterFilter['Start Time'].dt.month == myFilters[1]]

        elif myFilters[0] is not None:  # Applying Day Filter
            numAppliedFilters += 1
            dataAfterFilter = dataToApply.loc[dataToApply['Start Day Name'] == myFilters[0]]
            dataAfterFilter.append(dataToApply.loc[dataToApply['End Day Name'] == myFilters[0]])

        elif myFilters[1] is not None:  # Applying Month Filter
            dataAfterFilter = dataToApply.loc[dataToApply['Start Time'].dt.month == myFilters[1]]
            dataAfterFilter.append(dataToApply.loc[dataToApply['End Time'].dt.month == myFilters[1]])
        else:
            dataAfterFilter = dataToApply
        dataAfterFilter['Start Hour'] = dataAfterFilter['Start Time'].dt.hour
        dataAfterFilter['End Hour'] = dataAfterFilter['End Time'].dt.hour
        dataAfterFilter['Trip'] = dataAfterFilter['Start Station'] + " to " + dataAfterFilter['End Station']
        try:
            dataAfterFilter['Gender'] = dataAfterFilter['Gender'].replace(np.nan, "Unknown")
            dataAfterFilter['Birth Year'] = dataAfterFilter['Birth Year'].replace(np.nan, dataAfterFilter['Birth Year'].median())
        except KeyError:
            pass

        print("Filters Applied, This Operation took:", time.time()-t0)

        try:
            t0 = time.time()
            print("="*100)
            print("Calculating first Statistic (Hour)")
            mostCommonStart = dataAfterFilter['Start Hour'].mode()[0]
            mostCommonEnd = dataAfterFilter['End Hour'].mode()[0]
            startCount = dataAfterFilter['Start Hour'].value_counts()[mostCommonStart]
            endCount = dataAfterFilter['End Hour'].value_counts()[mostCommonEnd]
            print("Most Common Start Hour:", mostCommonStart, "|| Count:", startCount)
            print("Most Common End Hour:", mostCommonEnd, "|| Count:", endCount)
            print("That took:", time.time() - t0, "seconds")
        except KeyError:
            print("This data set Has no data on starting & ending hours")

        try:
            t0 = time.time()
            print("=" * 100)
            print("Calculating second Statistic (Trip Duration)")
            print("Total Trip Duration:", dataAfterFilter['Trip Duration'].sum())
            count = dataAfterFilter['Trip Duration'].count()
            print("Count:", count)
            print("Average Duration:", dataAfterFilter['Trip Duration'].mean())
            print("That took:", time.time() - t0, "seconds")
        except KeyError:
            print("This data set Has no data on Trip Duration")

        try:
            t0 = time.time()
            print("=" * 100)
            print("Calculating Third Statistic (Station)")
            mostCommonStart = dataAfterFilter['Start Station'].mode()[0]
            mostCommonEnd = dataAfterFilter['End Station'].mode()[0]
            startCount = dataAfterFilter['Start Station'].value_counts()[mostCommonStart]
            endCount = dataAfterFilter['End Station'].value_counts()[mostCommonEnd]
            print("Most Common Start Station:", mostCommonStart, "|| Count:", startCount)
            print("Most Common End Station:", mostCommonEnd, "|| Count:", endCount)
            print("That took:", time.time() - t0, "seconds")
        except KeyError:
            print("This data set Has no data on Station")

        try:
            t0 = time.time()
            print("="*100)
            print("Calculating Fourth Statistic (Trip)")
            mostCommonTrip = dataAfterFilter['Trip'].mode()[0]
            count = dataAfterFilter['Trip'].value_counts()[mostCommonTrip]
            print("Most Common Trip:", mostCommonTrip)
            print("Count:", count)
            print("That took:", time.time() - t0, "seconds")
        except KeyError:
            print("This data set Has no data on Trip")

        try:
            t0 = time.time()
            print("=" * 100)
            print("Calculating Fifth Statistic (User Type)")
            userTypes = dataAfterFilter['User Type'].value_counts()
            print(userTypes)
            print("That took:", time.time() - t0, "seconds")
        except KeyError:
            print("This data set Has no data on User Type")

        try:
            t0 = time.time()
            print("=" * 100)
            print("Calculating Sixth Statistic (Gender)")
            gender = dataAfterFilter['Gender'].value_counts()
            print(gender)
            print("That took:", time.time() - t0, "seconds")
        except KeyError:
            print("This data set Has no data on Gender")

        try:
            t0 = time.time()
            print("=" * 100)
            print("Calculating Seventh Statistic (Birth Year)")
            mostCommon = dataAfterFilter['Birth Year'].mode()[0]
            print("Most Common Birth Year:", mostCommon)
            count = dataAfterFilter['Birth Year'].value_counts()[mostCommon]
            print("Count:", count)
            print("Average Year of Birth:", dataAfterFilter['Birth Year'].mean())
            print("That took:", time.time() - t0, "seconds")
        except KeyError:
            print("This data set has no data on birth year")
        finally:
            print("=" * 100)

        i = 0
        j = 10
        cont = True
        while i < 300000 and cont:
            print("Showing first 10 rows of the data")
            pd.set_option("display.max_rows", None, "display.max_columns", None)
            print(dataAfterFilter[i:j])
            print("=" * 100)
            while True:
                z = input("Would you like to see more ? (y/n)\n->")
                if z != 'y' and z != 'n':
                    continue
                break
            cont = z.strip().lower() == 'y'
            i += 10
            j += 10
        while True:
            z = input("Restart ? (y/n)\n->")
            if z != 'y' and z != 'n':
                continue
            break
        start = z.strip().lower() == 'y'
