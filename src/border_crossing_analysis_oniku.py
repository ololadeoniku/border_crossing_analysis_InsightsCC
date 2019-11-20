# import the necessary builtin module, python builtin module for reading csv
import csv
import operator
from collections import Counter
from itertools import groupby
from operator import itemgetter
#########################################################
# store the input file in a variable "input_file"
input_file = "input/Border_Crossing_Entry_Data.csv"

# open input_file as "csv_input" then store in file object "input_reader" as a dictionary
with open(input_file, newline='') as csv_input:
    input_reader = csv.DictReader(csv_input)

# create an empty dictionary to store all the rows
    row_dictionary = {}

# read in each row into the dictionary, only read columns of interest, ["Port", "Border", "Date", "Measure", "Value"]
    for i, row in enumerate(input_reader):
        row_dictionary[i+1] = row["Port Name"],row["Border"],row["Date"],row["Measure"],row["Value"]
#########################################################
# create a class for the dictionary
class BorderEntry(dict):
    '''
    A class to hold all of the dictionary data on border crossing. Will subsequently add methods to perform desired operations like adding new ports
    '''

# initialize the class as a dictionary
    def __init__(self):
        self = dict()

    def add_port(self, port, border, date, measure, value):
        '''
        a method to add new ports (i.e rows). The method will take in variables port, border, date, measure and value. "port" will be used as dictionary key
        '''
        self[port] = border, date, measure, value

# method to compute number of rows in the dictionary
    def len(self):
        return self.__len__()

# method to sort items in the dictionary
    def sort_items(self, sort_key=0, is_reverse=False, is_integer=False):
        '''
        sort_key argument is the index of the column to sort by.
        is_reverse=False if Ascending order, and True if Descending order.
        is_integer argument will ensure numeric data are treated as numeric.
        '''
        if is_integer:
            return sorted(self, key=lambda port: int(self[port][sort_key]), reverse=is_reverse)
        else:
            return sorted(self, key=lambda port: self[port][sort_key], reverse=is_reverse)

# method to delete a row from the dictionary
    def del_row(self, row_key):
        self.pop(row_key, None)
        return self
        # return repr(dict(self))

# print method of the dictionary
    def __repr__(self):
        return repr(dict(self))
#########################################################
# instantiate the BorderEntry class as ports
ports = BorderEntry()

# loop through the dictionary to add each port (row) to the BorderEntry class
for k, v in row_dictionary.items():
    port = v[0]
    border = v[1]
    date = v[2]
    measure = v[3]
    value = v[4]
    ports.add_port(port,border, date, measure, value)
###########################################################
# create a "group" list and a function to respectively store and sort the dictionary by Date and Measure
groups = []
uniquekeys = []

def key_function(port):
    # key for sorting by Date
    key1 = ports[port][1]
    # key for sorting by Measure
    key2 = ports[port][2]
    # key for sorting by Value
    return (key1, key2)

# sort the dictionary by the key_function
ports_sorted = sorted(ports, key=lambda port: key_function(port), reverse=True)
# print(ports_sorted)
########################################################
# aggregate the dictionary by Date-Measure
for k, g in groupby(ports_sorted, key=lambda port:key_function(port)):
    groups.append(list(g))
    uniquekeys.append(k)
# print(uniquekeys, groups)

# Border-Measure grouping
grouping = [x for x in groups]
# print(grouping)

# group Values and Border together to later join with Date-Measure combinaation.
def group_items(j,l):
    '''
    j is index of Values in the dictionary and l is the index of Border in the dictionary
    '''
    grouped_item = []
    for x in grouping:
        if len(x) == 1:
            port = ports[x[0]]
            value_ = int(port[j])
            border_ = port[l]
            grouped_item.append((value_, border_))

        else:
            port = [ports[x[0]], ports[x[1]]]
            value_ = int(port[0][j]) + int(port[1][j])
            border_ = port[0][l]
            grouped_item.append((value_, border_))
    return grouped_item

grouped_items =group_items(3, 0)
group_length = len(grouped_items)
######################################################
# join all groupings together
grouped_dict = {}
for i, v, y in zip(range(1,group_length+1), uniquekeys, grouped_items):
    grouped_dict[i] = list((v, y))

all_group = [list(i[0])+list(i[1]) for i in grouped_dict.values()]

# sort by Date and Value after being grouped
sorted_group = sorted(all_group, key=itemgetter(0,2), reverse=False)
# add an extra column average to populate later
for i in sorted_group:
    i.append(0)

#########################################################
# create new dictionaries of the sorted dictionary columns
dates = Counter()
measures = Counter()
values = Counter()
borders = Counter()
average = Counter()

for i, v in enumerate(sorted_group):
    dates[i] = v[0]
    measures[i] = v[1]
    values[i] = v[2]
    borders[i] = v[3]
    average[i] = v[4]
############################################################
# use counters to keep track of multiple instances of the "Measure" columns
multiples = Counter(measures.values())
multiple_measure = {k:v for k,v in measures.items() if multiples[v] > 1}

date_min = min(dates.values())
date_max = max(dates.values())


##########################################################
# use conditionals to populate the average column
count_value = 0
counter = 0
for i,v in multiple_measure.items():
    count_value = count_value + values[i]
    counter = counter+1
    if dates[i] == date_min:
        sorted_group[i][4] = 0
    else:
        sorted_group[i][4] = round((count_value - values[i])/(counter-1))
###########################################################
# final sorting of dictionary output
final_sort = sorted(sorted_group, key=itemgetter(0,2,1,3), reverse=True)

#############################################################
#convert to dictionary and add column names
final_output = {}
column_names = ["Date", "Measure", "Value", "Border", "Average"]
for i, r in zip(final_sort, range(len(final_sort))):
    column = {j:i[k] for k,j in enumerate(column_names)}
    final_output[r] = column

final = final_output.values()
#############################################################
#export to csv
with open("output/report.csv", "w", newline='') as csvfile:
    #rearrange field names
    field_names = ["Border", "Date", "Measure", "Value", "Average"]
    csv_writer = csv.DictWriter(csvfile, fieldnames=field_names)
# write the column names
    csv_writer.writeheader()
#add each row in the dictionary to the writer
    for row in final:
        csv_writer.writerow(row)
