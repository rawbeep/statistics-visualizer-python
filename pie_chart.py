import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ==============================================================================
# PART 1: LOADING THE DATA
# We do this first so the data is ready before we try to make any charts.
# ==============================================================================
try:
    # Try to read the CSV file
    df = pd.read_csv("project.csv")

    # 1. CLEANING: Sometimes Excel adds a weird empty column at the end.
    # If we see 'Unnamed: 1', we just delete it.
    if 'Unnamed: 1' in df.columns:
        df = df.drop(columns=['Unnamed: 1'])

    # 2. CLEANING: Drop rows that are completely empty so they don't mess up the math
    df = df.dropna(how='all')

    # 3. CLEANING: Make sure the names are text (strings), not numbers
    df['student name'] = df['student name'].astype(str)

    print("✓ Success: project.csv loaded!")
    # This helps us see which columns are actually numbers (grades)
    grade_columns = list(df.select_dtypes(include=[np.number]).columns)
    print(f"  Found these subjects: {grade_columns}")

except Exception as e:
    # If something goes wrong (like file not found), print the error
    print(f"❌ Error: Could not load data. Details: {e}")
    # Create fake data just so the app doesn't crash while we are testing it
    df = pd.DataFrame({
        'student name': ['Student A', 'Student B'],
        'MATH': [50, 60],
        'CS101': [80, 90]
    })


# --- HELPER FUNCTION ---
# This saves us time. If we don't ask for specific subjects,
# this function just grabs ALL the numeric columns for us.
def get_subject_list(df, subjects=None):
    if subjects is None:
        return df.select_dtypes(include=[np.number]).columns.tolist()
    return subjects


# ==============================================================================
# PART 2: THE GRAPHS (The Tools)
# ==============================================================================

# 📊 GRAPH 1: HISTOGRAM
# Purpose: Shows the "Curve". Did most people get A's or F's?
def draw_histogram(df, subject_name):
    fig = plt.figure(figsize=(6, 4))

    # Only draw if the column actually exists
    if subject_name in df.columns:
        scores = df[subject_name].dropna()  # Remove empty scores

        # Plotting: Using SteelBlue for a professional look
        plt.hist(scores, bins=10, range=(0, 100), color='#5DADE2', edgecolor='slategrey')

        plt.title(f"Grade Distribution: {subject_name}")
        plt.xlabel("Score")
        plt.ylabel("Number of Students")
    else:
        plt.text(0.5, 0.5, "Subject Not Found", ha='center')

    return fig


# 🟢 GRAPH 2: PASS/FAIL PIE CHART
# Purpose: A quick check to see the percentage of students who passed.
def draw_pass_fail(df, subject_name):
    fig = plt.figure(figsize=(6, 5))

    if subject_name not in df.columns:
        return fig

    # We assume 50 is the passing grade
    passed = len(df[df[subject_name] >= 50])
    failed = len(df[df[subject_name] < 50])

    # If no data, don't try to draw a chart
    if passed + failed == 0:
        return fig

    # COLORS: Blue for Pass, Grey for Fail (Cleaner look)
    my_colors = ['#5DADE2', '#D5D8DC']  # Steel Blue & Light Grey

    plt.pie([passed, failed], labels=[f'Pass ({passed})', f'Fail ({failed})'],
            colors=my_colors, autopct='%1.1f%%', startangle=90)

    plt.title(f"Pass Rate: {subject_name}")
    return fig


# ⚖️ GRAPH 3: BAR COMPARISON
# Purpose: Compare averages to see which subject was the hardest.
# You can give it a specific list of subjects, or leave it empty to compare ALL.
def draw_comparison(df, subjects_to_compare=None):
    fig = plt.figure(figsize=(8, 5))

    # Get the list of subjects we want to graph
    subjects = get_subject_list(df, subjects_to_compare)

    # Calculate the average (mean) for each
    averages = df[subjects].mean()

    # LOGIC: If average is low (<50), make it Grey. If good, make it Blue.
    # This highlights the "problem" subjects without being too aggressive.
    colors = ['#B0B3B8' if x < 50 else '#5DADE2' for x in averages]

    bars = plt.bar(subjects, averages, color=colors, edgecolor='slategrey')

    # Put the score number on top of each bar so it's easy to read
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 f'{bar.get_height():.0f}', ha='center', va='bottom')

    plt.title("Subject Difficulty Comparison")
    plt.ylim(0, 110)  # Set height to 110 so labels fit
    return fig


# 🏆 GRAPH 4: TOP vs BOTTOM
# Purpose: Identifies the highest achievers and those who need help.
def draw_top_bottom(df):
    fig = plt.figure(figsize=(8, 6))

    # 1. Calculate the 'Overall Average' for every student
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    temp_df = df.copy()
    temp_df['Average'] = temp_df[numeric_cols].mean(axis=1)

    # 2. Sort the list from lowest to highest
    temp_df = temp_df.sort_values('Average')

    # 3. Grab the Bottom 5 and Top 5
    combined = pd.concat([temp_df.head(5), temp_df.tail(5)])

    # COLORS: Grey for bottom (needs improvement), Blue for top
    colors = ['#B0B3B8'] * 5 + ['#5DADE2'] * 5

    plt.barh(combined['student name'], combined['Average'], color=colors, edgecolor='slategrey')
    plt.title("Top 5 vs Bottom 5 Students")
    plt.xlabel("Overall Average Score")
    return fig


# 📦 GRAPH 5: BOX PLOT
# Purpose: Shows consistency. A big box means grades are all over the place.
def draw_boxplot(df, subjects_to_compare=None):
    fig = plt.figure(figsize=(8, 5))
    subjects = get_subject_list(df, subjects_to_compare)

    # Prepare the data (drop empty cells so it doesn't crash)
    data = [df[sub].dropna() for sub in subjects]

    # Draw it with our color theme
    plt.boxplot(data, labels=subjects, patch_artist=True,
                boxprops=dict(facecolor='#AED6F1', color='slategrey'),  # Light Blue box
                medianprops=dict(color='#2E86C1', linewidth=2))  # Dark Blue line

    plt.title("Grade Consistency (Range)")
    plt.grid(axis='y', alpha=0.3)
    return fig


# 📈 GRAPH 6: TREND LINE
# Purpose: Shows if the class is doing better or worse across subjects.
def draw_trend(df, subjects_in_order=None):
    fig = plt.figure(figsize=(8, 5))
    subjects = get_subject_list(df, subjects_in_order)

    averages = df[subjects].mean()

    # Plot line with Steel Blue
    plt.plot(subjects, averages, marker='o', linewidth=3, color='#2874A6')

    # Add a soft blue fill under the line
    plt.fill_between(subjects, averages, color='#5DADE2', alpha=0.2)

    plt.title("Performance Trend Overview")
    plt.ylim(0, 100)
    return fig


# ==============================================================================
# PART 3: TEST AREA
# This runs if you just open this file directly.
# It simulates what happens when you click buttons in the GUI.
# ==============================================================================
if __name__ == "__main__":
    print("\n--- TESTING THE CHARTS ---\n")

    # Example 1: Show Math Pass/Fail
    print("Test 1: Showing Math Pie Chart...")
    fig1 = draw_pass_fail(df, "MATH")
    plt.show()

    # Example 2: Compare specific subjects
    print("Test 2: Comparing CS subjects...")
    fig3 = draw_comparison(df, ["CS101", "CS102"])
    plt.show()

    print("\n✓ All charts generated successfully.")