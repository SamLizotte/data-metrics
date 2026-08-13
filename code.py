import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# importing and opening dataset, code is going to assume data is already in csv
df = pd.read_csv(r"funnel clean final.csv", na_values=["N/A", "Unknown"])

# counting number of rows and columns
rows, columns = df.shape[0], df.shape[1]

# counting nulls 
null_count_col = df.isnull().sum()
null_count_tot = null_count_col.sum()

# look at the type of each column
data_types = df.dtypes

# channel
channel = df['Channel'].value_counts()
channel_choose = input(f"Choose a channel to plot from the following options: {list(channel.index)}\nEnter the channel name (case-sensitive): ")
df_filtered = df[df['Channel'] == channel_choose]

# columns
col_titles = list(df.columns)

# selecting numeric columns for graphing
numeric_cols = df.select_dtypes(int).columns
if len(numeric_cols) == 0:
    raise ValueError("No numeric columns available for a histogram.")
numeric_cols = numeric_cols[1:]

#descriptive statistics for the entire dataset
descriptors = df.describe()

# find outliers based on standard deviation, set optional multiplier that automatically resets to 1.96 if not provided
def find_outliers(column_name, multiplier=1.96):
    dataset = df[column_name]
    if not multiplier:
        multiplier = 1.96
    else:
        multiplier = float(multiplier)
    mu = np.mean(dataset)
    sigma = np.std(dataset)
    # standard deviation multiplier for outlier detection, can be adjusted
    limit = sigma * multiplier
    
    min_threshold = mu - limit
    max_threshold = mu + limit
    
    # Make sure this returns a boolean mask the SAME length as dataset
    outlier_mask = (dataset < min_threshold) | (dataset > max_threshold) 
    return outlier_mask


# without filtered by group selection
# prompt user to ask for a column to plot histogram
print(f"Numeric columns available for histogram: {numeric_cols}")
print("Choose a numeric column to plot a histogram from the list above.")
chosen_col_hist = input("Enter the column name (case-sensitive): ")
# plot histogram
df[chosen_col_hist].plot.hist(xlabel=chosen_col_hist, bins=20, title=f"Histogram of {chosen_col_hist}")
plt.show()


# prompt user to ask for a column to plot scatter plot -- no outliers
print(f"Numeric columns available for scatter plot: {numeric_cols}")
print("Choose two numeric columns to plot a scatter plot from the list above.")
line_col_1 = input("Enter the x column name (case-sensitive): ")
line_col_2 = input("Enter the y column name (case-sensitive): ")
# plot scatter plot
df.plot(x=line_col_1, y=line_col_2, xlabel=line_col_1, ylabel=line_col_2, title=f"Scatter plot of {line_col_1} vs {line_col_2}", kind='scatter')
plt.show()


# prompt user to ask for a column to plot scatter plot -- outliers
print(f"Numeric columns available for scatter plot: {numeric_cols}")
print("Choose two numeric columns to plot a scatter plot from the list above.")
line_col_1 = input("Enter the x column name (case-sensitive): ")
line_col_2 = input("Enter the y column name (case-sensitive): ")
multiplier = input("Enter the multiplier for standard deviation (default is 1.96, approx 95% confidence): ")
outlier_1 = find_outliers(line_col_1, multiplier)
outlier_2 = find_outliers(line_col_2, multiplier)
# Different categories
normal = ~outlier_1 & ~outlier_2  # Not outlier in either
outlier_x_only = outlier_1 & ~outlier_2  # Outlier only in x
outlier_y_only = ~outlier_1 & outlier_2  # Outlier only in y
outlier_both = outlier_1 & outlier_2  # Outlier in both

# Normal points
plt.scatter(df[normal][line_col_1], df[normal][line_col_2],
            color='blue', label='Normal', alpha=0.6)

# Outlier in x only
plt.scatter(df[outlier_x_only][line_col_1], df[outlier_x_only][line_col_2],
            color='orange', label=f'Outlier in {line_col_1} only', s=80, edgecolors='black', linewidth=1)

# Outlier in y only
plt.scatter(df[outlier_y_only][line_col_1], df[outlier_y_only][line_col_2],
            color='green', label=f'Outlier in {line_col_2} only', s=80, edgecolors='black', linewidth=1)

# Outlier in both
plt.scatter(df[outlier_both][line_col_1], df[outlier_both][line_col_2],
            color='red', label=f'Outlier in {line_col_1} and {line_col_2}', s=120, edgecolors='black', linewidth=2)

plt.xlabel(line_col_1)
plt.ylabel(line_col_2)
plt.title(f"Scatter plot of {line_col_1} vs {line_col_2}")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()


# prompt user to ask for a column to plot line chart
print(f"Numeric columns available for line chart: {numeric_cols}")
print("Choose a numeric column to plot a line chart from the list above.")
# turn date strings into datetime objects
line_col_2 = input("Enter the y column name (case-sensitive): ")
# plot line chart
df.plot(x=numeric_cols[0], y=line_col_2, xlabel=numeric_cols[0], ylabel=line_col_2, title=f"Line chart of {numeric_cols[0]} vs {line_col_2}", kind='line')
plt.show()






# with filtered by group selection

filt_desc = df_filtered.describe()
filt_col_title = list(df_filtered.columns)

# filtered numeric columns for graphing
numeric_cols_filt = df_filtered.select_dtypes(int).columns
if len(numeric_cols_filt) == 0:
    raise ValueError("No numeric columns available for a histogram.")
numeric_cols_filt = numeric_cols_filt[1:]


# prompt user to ask for a column to plot histogram
print(f"Numeric columns available for histogram: {numeric_cols_filt}")
print("Choose a numeric column to plot a histogram from the list above.")
chosen_col_hist = input("Enter the column name (case-sensitive): ")
# plot histogram
df_filtered[chosen_col_hist].plot.hist(xlabel=chosen_col_hist, bins=20, title=f"Histogram of {chosen_col_hist} by {channel_choose}")
plt.show()


# prompt user to ask for a column to plot scatter plot -- no outliers
print(f"Numeric columns available for scatter plot: {numeric_cols_filt}")
print("Choose two numeric columns to plot a scatter plot from the list above.")
line_col_1 = input("Enter the x column name (case-sensitive): ")
line_col_2 = input("Enter the y column name (case-sensitive): ")
# plot scatter plot
df_filtered.plot(x=line_col_1, y=line_col_2, xlabel=line_col_1, ylabel=line_col_2, title=f"Scatter plot of {line_col_1} vs {line_col_2} by {channel_choose}", kind='scatter')
plt.show()


# prompt user to ask for a column to plot scatter plot -- outliers
print(f"Numeric columns available for scatter plot: {numeric_cols_filt}")
print("Choose two numeric columns to plot a scatter plot from the list above.")
line_col_1 = input("Enter the x column name (case-sensitive): ")
line_col_2 = input("Enter the y column name (case-sensitive): ")
multiplier = input("Enter the multiplier for standard deviation (default is 1.96, approx 95% confidence): ")
outlier_1 = find_outliers(line_col_1, multiplier)
outlier_2 = find_outliers(line_col_2, multiplier)
# Different categories
normal = ~outlier_1 & ~outlier_2  # Not outlier in either
outlier_x_only = outlier_1 & ~outlier_2  # Outlier only in x
outlier_y_only = ~outlier_1 & outlier_2  # Outlier only in y
outlier_both = outlier_1 & outlier_2  # Outlier in both

# Normal points
plt.scatter(df_filtered[normal][line_col_1], df_filtered[normal][line_col_2],
            color='blue', label='Normal', alpha=0.6)

# Outlier in x only
plt.scatter(df_filtered[outlier_x_only][line_col_1], df_filtered[outlier_x_only][line_col_2],
            color='orange', label='Outlier in X only', s=80, edgecolors='black', linewidth=1)

# Outlier in y only
plt.scatter(df_filtered[outlier_y_only][line_col_1], df_filtered[outlier_y_only][line_col_2],
            color='green', label='Outlier in Y only', s=80, edgecolors='black', linewidth=1)

# Outlier in both
plt.scatter(df_filtered[outlier_both][line_col_1], df_filtered[outlier_both][line_col_2],
            color='red', label='Outlier in Both', s=120, edgecolors='black', linewidth=2)

plt.xlabel(line_col_1)
plt.ylabel(line_col_2)
plt.title(f"Scatter plot of {line_col_1} vs {line_col_2}")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()


# prompt user to ask for a column to plot line chart
print(f"Numeric columns available for line chart: {numeric_cols_filt}")
print("Choose a numeric column to plot a line chart from the list above.")
# turn date strings into datetime objects
line_col_2 = input("Enter the y column name (case-sensitive): ")
# plot line chart
df_filtered.plot(x=filt_col_title[1], y=line_col_2, xlabel=filt_col_title[1], ylabel=line_col_2, title=f"Line chart of {filt_col_title[1]} vs {line_col_2} by {channel_choose}", kind='line')
plt.show()