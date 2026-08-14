import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

st.title("Metric Dashboard")

# importing and opening dataset, code is going to assume data is already in csv
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write(df.head(50))

    # counting number of rows and columns
    rows, columns = df.shape[0], df.shape[1]

    # columns
    col_titles = list(df.columns)

    # counting nulls 
    null_count_col = df.isnull().sum()
    null_count_tot = null_count_col.sum()

    # look at the type of each column
    data_types = df.dtypes

    # Initialize session state
    if 'group_column' not in st.session_state:
        st.session_state.group_column = None  # Start with None (optional)
        
    if 'channel_choose' not in st.session_state:
        st.session_state.channel_choose = None

    # First menu - choose column/group (optional)
    group = st.menu_button(
        "What column/group do you want to sort by? (Optional)", 
        ["None"] + col_titles  # Add "None" as first option
    )

    # Update session state
    if group is not None:
        if group == "None":
            st.session_state.group_column = None
            st.session_state.channel_choose = None  # Reset channel too
        else:
            st.session_state.group_column = group
            st.session_state.channel_choose = None

    # SAFELY get group options
    if st.session_state.group_column is not None:
        group_options = df[st.session_state.group_column].unique().tolist()
        # Add "All" option to show everything
        group_options = ["All"] + group_options
    else:
        group_options = []
        st.info("No group selected - showing all data")

    st.write("Optional sort by group:")

    # Second menu - only show if group is selected
    if st.session_state.group_column is not None and group_options:
        channel_choose = st.menu_button("Group (Optional)", group_options)
        
        if channel_choose is not None:
            st.session_state.channel_choose = channel_choose
        
        # Display current selection
        if st.session_state.channel_choose:
            if st.session_state.channel_choose == "All":
                st.write("Showing all groups")
            else:
                st.write(f"{st.session_state.channel_choose} is currently selected as your group.")
    else:
        st.info("Select a group column first or leave as 'None' to see all data")

    # Filter dataframe
    if (st.session_state.group_column is not None and 
        st.session_state.channel_choose is not None and
        st.session_state.channel_choose != "All"):
        df_filtered = df[df[st.session_state.group_column] == st.session_state.channel_choose]
    elif st.session_state.group_column is None:
        df_filtered = df  # Show all data
    else:
        df_filtered = df  # Show all data if "All" selected

    # selecting numeric columns for graphing
    numeric_cols = df.select_dtypes(int).columns
    if len(numeric_cols) == 0:
        raise ValueError("No numeric columns available for a histogram.")
    numeric_cols = numeric_cols[1:]

    #descriptive statistics for the entire dataset
    if st.button("See general statistics?"):
        descriptors = df_filtered.describe()
        st.write(descriptors)

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

    filt_desc = df_filtered.describe()
    filt_col_title = list(df_filtered.columns)

    # filtered numeric columns for graphing
    numeric_cols_filt = df_filtered.select_dtypes(int).columns
    if len(numeric_cols_filt) == 0:
        raise ValueError("No numeric columns available for a histogram.")
    numeric_cols_filt = numeric_cols_filt[1:]

    graph_prompt = st.multiselect("Choose a graph", ["Histogram", "Scatterplot", "Line Chart", "Correlation Matrix"])
    if "Histogram" in graph_prompt:
        # Use selectbox instead of menu_button for a single selection
        # We assign the result to a temporary variable first
        user_selection = st.selectbox(
            "Data to plot histograms", 
            numeric_cols_filt, 
            key="hist_select"
        )
        # Update the session state with whatever the user just selected
        st.session_state.chosen_column = user_selection

        # Now you can safely use the session state value
        if st.session_state.chosen_column is not None:
            data = df_filtered[st.session_state.chosen_column]
            
            num_bins = st.slider("Number of bins", min_value=1, max_value=50, value=10)
            
            fig, ax = plt.subplots()
            ax.hist(data, bins=num_bins, edgecolor=None)
            ax.set_title(f"Histogram of {st.session_state.chosen_column}")
            ax.set_xlabel(st.session_state.chosen_column)
            ax.set_ylabel("Frequency")
            
            st.pyplot(fig)

    if "Scatterplot" in graph_prompt:

        # Convert to list if it's a pandas Index
        if isinstance(numeric_cols_filt, pd.Index):
            numeric_cols_list = numeric_cols_filt.tolist()
        else:
            numeric_cols_list = list(numeric_cols_filt) if numeric_cols_filt else []

        # Initialize session state
        if 'scatter_col_1' not in st.session_state:
            # Check if list has elements before accessing
            if len(numeric_cols_list) > 0:
                st.session_state.scatter_col_1 = numeric_cols_list[0]
            else:
                st.session_state.scatter_col_1 = None
                st.error("No numeric columns available for plotting")
            
        if 'scatter_col_2' not in st.session_state:
            if len(numeric_cols_list) > 1:
                st.session_state.scatter_col_2 = numeric_cols_list[1]
            elif len(numeric_cols_list) == 1:
                st.session_state.scatter_col_2 = numeric_cols_list[0]
            else:
                st.session_state.scatter_col_2 = None

        if 'show_outliers' not in st.session_state:
            st.session_state.show_outliers = False

        if 'multiplier' not in st.session_state:
            st.session_state.multiplier = 1.96

        # Validate selections still exist in the current list
        if st.session_state.scatter_col_1 not in numeric_cols_list and len(numeric_cols_list) > 0:
            st.session_state.scatter_col_1 = numeric_cols_list[0]

        if st.session_state.scatter_col_2 not in numeric_cols_list and len(numeric_cols_list) > 0:
            st.session_state.scatter_col_2 = numeric_cols_list[0]

        # Only show menus if there are columns to select
        if len(numeric_cols_list) > 0:
            # Prompt user to ask for a column to plot scatter plot
            scatter_col_1 = st.menu_button("Choose the x-value", numeric_cols_list, key="scatter1")
            
            # Update session state
            if scatter_col_1 is not None:
                st.session_state.scatter_col_1 = scatter_col_1
            
            scatter_col_2 = st.menu_button("Choose the y-value", numeric_cols_list,key="scatter2")
            
            # Update session state
            if scatter_col_2 is not None:
                st.session_state.scatter_col_2 = scatter_col_2
            
            # Display current selection using session state
            st.write(f"You've chosen {st.session_state.scatter_col_1} as your x-value and {st.session_state.scatter_col_2} as your y-value.")
            
            # Outlier toggle with state
            st.write("Do you want to see outliers?")
            
            # Use toggle to maintain state
            show_outliers = st.toggle(
                "Show outliers",
                value=st.session_state.show_outliers,
                key="outlier_toggle"
            )
            st.session_state.show_outliers = show_outliers
            
            # Display content based on state
            if st.session_state.show_outliers:
                # prompt user to ask for a column to plot scatter plot -- outliers
                multiplier = st.number_input(
                    "Input the multiplier you want to calculate outlier with (standard is 1.96):",
                    value=st.session_state.multiplier,
                    min_value=0.0,
                    max_value=10.0,
                    step=0.01,
                    key="multiplier_input"
                )
                st.session_state.multiplier = multiplier
                
                # Make sure we have valid column names
                if st.session_state.scatter_col_1 and st.session_state.scatter_col_2:
                    outlier_1 = find_outliers(st.session_state.scatter_col_1, multiplier)
                    outlier_2 = find_outliers(st.session_state.scatter_col_2, multiplier)
                    
                    # Different categories
                    normal = ~outlier_1 & ~outlier_2  # Not outlier in either
                    outlier_x_only = outlier_1 & ~outlier_2  # Outlier only in x
                    outlier_y_only = ~outlier_1 & outlier_2  # Outlier only in y
                    outlier_both = outlier_1 & outlier_2  # Outlier in both
                    
                    # Create figure
                    fig, ax = plt.subplots()
                    
                    # Normal points
                    ax.scatter(df_filtered[normal][st.session_state.scatter_col_1], 
                            df_filtered[normal][st.session_state.scatter_col_2],
                            color='blue', label='Normal', alpha=0.6)
                    
                    # Outlier in x only
                    ax.scatter(df_filtered[outlier_x_only][st.session_state.scatter_col_1], 
                            df_filtered[outlier_x_only][st.session_state.scatter_col_2],
                            color='orange', label='Outlier in X only', s=80, edgecolors='black', linewidth=1)
                    
                    # Outlier in y only
                    ax.scatter(df_filtered[outlier_y_only][st.session_state.scatter_col_1], 
                            df_filtered[outlier_y_only][st.session_state.scatter_col_2],
                            color='green', label='Outlier in Y only', s=80, edgecolors='black', linewidth=1)
                    
                    # Outlier in both
                    ax.scatter(df_filtered[outlier_both][st.session_state.scatter_col_1], 
                            df_filtered[outlier_both][st.session_state.scatter_col_2],
                            color='red', label='Outlier in Both', s=120, edgecolors='black', linewidth=2)
                    
                    ax.set_xlabel(st.session_state.scatter_col_1)
                    ax.set_ylabel(st.session_state.scatter_col_2)
                    ax.set_title(f"Scatter plot of {st.session_state.scatter_col_1} vs {st.session_state.scatter_col_2}")
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    st.pyplot(fig)
                else:
                    st.warning("Please select both x and y values")
            
            else:
                # plot scatter plot without outliers
                if st.session_state.scatter_col_1 and st.session_state.scatter_col_2:
                    # Use matplotlib's scatter
                    fig, ax = plt.subplots()
                    
                    # Note: For plt.scatter, first argument is x, second is y
                    ax.scatter(
                        df_filtered[st.session_state.scatter_col_1],  # x values
                        df_filtered[st.session_state.scatter_col_2],  # y values
                        alpha=0.6,
                        color='blue'
                    )
                    
                    ax.set_xlabel(st.session_state.scatter_col_1)
                    ax.set_ylabel(st.session_state.scatter_col_2)
                    ax.set_title(f"Scatter plot of {st.session_state.scatter_col_1} vs {st.session_state.scatter_col_2}")
                    ax.grid(True, alpha=0.3)
                    
                    st.pyplot(fig)
                else:
                    st.warning("Please select both x and y values")
        else:
            st.error("No numeric columns available for plotting. Please check your data.")

    if "Line Chart" in graph_prompt:
        # Convert to list if it's a pandas Index
        if isinstance(numeric_cols_filt, pd.Index):
            numeric_cols_list = numeric_cols_filt.tolist()
        else:
            numeric_cols_list = list(numeric_cols_filt) if numeric_cols_filt else []

        # Initialize session state
        if 'line_col_1' not in st.session_state:
            # Check if list has elements before accessing
            if len(numeric_cols_list) > 0:
                st.session_state.line_col_1 = numeric_cols_list[0]
            else:
                st.session_state.line_col_1 = None
                st.error("No numeric columns available for plotting")

        if 'line_col_2' not in st.session_state:
            if len(numeric_cols_list) > 1:
                st.session_state.line_col_2 = numeric_cols_list[1]
            elif len(numeric_cols_list) == 1:
                st.session_state.line_col_2 = numeric_cols_list[0]
            else:
                st.session_state.line_col_2 = None

        # Validate selections still exist in the current list
        if st.session_state.line_col_1 not in numeric_cols_list and len(numeric_cols_list) > 0:
            st.session_state.line_col_1 = numeric_cols_list[0]

        if st.session_state.line_col_2 not in numeric_cols_list and len(numeric_cols_list) > 0:
            st.session_state.line_col_2 = numeric_cols_list[0]

        # Only show menus if there are columns to select
        if len(numeric_cols_list) > 0:
            # Prompt user to ask for a column to plot line chart
            line_col_1 = st.menu_button("Choose the x-value", numeric_cols_list,key="line1")
            
            # Update session state
            if line_col_1 is not None:
                st.session_state.line_col_1 = line_col_1

            line_col_2 = st.menu_button("Choose the y-value", numeric_cols_list,key="line2")
            
            # Update session state
            if line_col_2 is not None:
                st.session_state.line_col_2 = line_col_2

            # Display current selection using session state
            st.write(f"You've chosen {st.session_state.line_col_1} as your x-value and {st.session_state.line_col_2} as your y-value")

            # Plot line chart
            if st.session_state.line_col_1 and st.session_state.line_col_2:
                # Option 1: Using pandas plot
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Sort by x-value for cleaner line chart
                df_sorted = df_filtered.sort_values(by=st.session_state.line_col_1)
                
                # Plot the line
                ax.plot(
                    df_sorted[st.session_state.line_col_1],
                    df_sorted[st.session_state.line_col_2],
                    marker='o',
                    linestyle='-',
                    linewidth=2,
                    markersize=6,
                    color='blue'
                )
                
                ax.set_xlabel(st.session_state.line_col_1)
                ax.set_ylabel(st.session_state.line_col_2)
                ax.set_title(f"Line chart of {st.session_state.line_col_2} vs {st.session_state.line_col_1}")
                ax.grid(True, alpha=0.3)
                
                st.pyplot(fig)
                
            else:
                st.warning("Please select both x and y values")
        else:
            st.error("No numeric columns available for plotting")

    if "Correlation Matrix" in graph_prompt:
        # 1. Select numeric columns
        df_num = df_filtered.select_dtypes(include=[np.number])
        
        # 2. Check if there are ANY numeric columns left to plot!
        if df_num.empty or len(df_num.columns) == 0:
            st.warning("No numeric columns available to plot a correlation matrix. Please check your data.")
        else:
            # Proceed only if there are columns to plot
            df_num = df_num.drop('Week', axis=1, errors='ignore')
            correlation = df_num.corr()

            # 3. Create annotation matrix
            annot_labels = correlation.astype(str)

            high_threshold = st.slider("High significance threshold", min_value=0.6, max_value=0.99, value=0.7)
            low_threshold = st.slider("Low significance threshold", min_value=-0.99, max_value=-0.6, value=-0.7)    

            for i in range(len(correlation.columns)):
                for j in range(len(correlation.columns)):
                    val = correlation.iloc[i, j].item()
                    
                    if val == 1.0: 
                        annot_labels.iloc[i, j] = f"{val:.2f}"
                    elif val > high_threshold or val < low_threshold:
                        annot_labels.iloc[i, j] = f"{val:.2f}*"
                    else:
                        annot_labels.iloc[i, j] = f"{val:.2f}"

            # 4. Clear the plot and draw
            plt.clf()
            plt.figure(figsize=(8,6))
            
            # If there's only 1 numeric column, heatmap will still be weird, but this prevents a crash
            if len(correlation.columns) < 2:
                st.info("Need at least 2 numeric columns to see a correlation.")
            else:
                sns.heatmap(correlation, annot=annot_labels, fmt='', cmap="coolwarm", linewidths=0.5)
                plt.title("Correlation Heatmap")
                st.pyplot(plt)

else:
    st.info("Please provide a dataset to begin.")