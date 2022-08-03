import re
import sqlite3
import csv
import pandas as pd
import matplotlib.pyplot as plt
from mlxtend.evaluate import permutation_test
import numpy as np

#
# xl_file = pd.ExcelFile("/Users/j-abbit/Documents/Bioinformatics_Thesis/Pub3.xlsx")
#
# dfs = pd.read_excel("/Users/j-abbit/Documents/Bioinformatics_Thesis/Pub3.xlsx")

#
# diff1=[]
# diff2=[]
# SubmissionDate=[]
# CollectionDate=[]
# publicationDate=[]
#
# for i in range(0,48):
#     diff1.append((dfs["SubmissionDate"][i] - dfs["CollectionDate"][i]).days)
#     diff2.append((dfs["publicationDate"][i] - dfs["CollectionDate"][i]).days)
#     SubmissionDate.append(dfs['SubmissionDate'][i])
#     CollectionDate.append(dfs['CollectionDate'][i])
#     publicationDate.append(dfs['publicationDate'][i])
#
#
# plt.hist(diff1)
# plt.show()
#
# plt.hist(diff2)
# plt.show()
#
# p_value1 = permutation_test(
#     diff1, diff2, paired=True, method="approximate", seed=0, num_rounds=100000
# )
# print(p_value1)
#
# variance1 = np.var(diff1)
# variance2 = np.var(diff2)
# print(variance1)
# print(variance2)
#
#

#
# # plt.plot(CollectionDate)
# plt.plot(SubmissionDate)
# plt.plot(publicationDate)
# plt.show()


