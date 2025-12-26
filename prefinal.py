#imports
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

root=tk.Tk()
root.title("grade statistics visualizer")
root.configure(bg='#3E3E3E')
root.state('zoomed')
# ensure root grid gives both rows and both columns expandable space
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
df = pd.read_csv(r"C:\Users\omark\OneDrive\Documents\cs102 project\project.csv")
# strip column names immediately and define subjects for the UI
df.columns = df.columns.str.strip()
subjects = ['CS101','CS102','ENG102','MATH','SSC1']
# ensure subject columns are numeric for plotting (harmless if repeated later)
for col in subjects:
    df[col] = pd.to_numeric(df[col], errors='coerce')
# graph UI: combobox above the graph to choose subject and a frame to host the canvas
buttons_frame = tk.Frame(root, bg='#3E3E3E')
buttons_frame.grid(row=0, column=1, sticky='ew', padx=10, pady=10)
# reserve columns for temp buttons + label + combobox
buttons_frame.grid_columnconfigure(0, weight=0)
buttons_frame.grid_columnconfigure(1, weight=0)
buttons_frame.grid_columnconfigure(2, weight=0)
buttons_frame.grid_columnconfigure(3, weight=1)

# temporary buttons placed to the left of the combo box
temp_btn1 = ttk.Button(buttons_frame, text="Graph 1")
temp_btn1.grid(row=0, column=0, padx=(0,6))
temp_btn2 = ttk.Button(buttons_frame, text="Graph 2")
temp_btn2.grid(row=0, column=1, padx=(0,6))

tk.Label(buttons_frame, text="Subject:", bg='#3E3E3E', fg='white').grid(row=0, column=2, sticky='w')
subject_var = tk.StringVar()
combo = ttk.Combobox(buttons_frame, textvariable=subject_var, values=subjects, state='readonly', width=12)
combo.grid(row=0, column=3, sticky='w', padx=(8,0))
combo.set(subjects[0])

graph_frame = tk.Frame(root, bg='#3E3E3E')
graph_frame.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')
graph_frame.grid_rowconfigure(0, weight=1)
graph_frame.grid_columnconfigure(0, weight=1)

# content_frame holds either the matplotlib canvas or a table view
content_frame = tk.Frame(graph_frame, bg='#3E3E3E')
content_frame.grid(row=0, column=0, sticky='nsew')
content_frame.grid_rowconfigure(0, weight=1)
content_frame.grid_columnconfigure(0, weight=1)

fig = Figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot(111)
canvas = None
view_mode = 'hist'  # add initial view mode

def clear_content_frame():
    for w in content_frame.winfo_children():
        w.destroy()

def display_graph():
    global canvas, view_mode
    view_mode = 'hist'
    clear_content_frame()
    canvas = FigureCanvasTkAgg(fig, master=content_frame)
    canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    content_frame.update_idletasks()

def display_table(df_subset, title):
    clear_content_frame()
    hdr = tk.Label(content_frame, text=title, bg='#3E3E3E', fg='white')
    hdr.grid(row=0, column=0, sticky='w', padx=5, pady=(5,0))
    tv_frame = tk.Frame(content_frame)
    tv_frame.grid(row=1, column=0, sticky='nsew')
    tv_frame.grid_rowconfigure(0, weight=1)
    tv_frame.grid_columnconfigure(0, weight=1)

    tv = ttk.Treeview(tv_frame, show='headings')
    tv.grid(row=0, column=0, sticky='nsew')

    # vertical scrollbar
    vs = ttk.Scrollbar(tv_frame, orient='vertical', command=tv.yview)
    vs.grid(row=0, column=1, sticky='ns')
    # horizontal scrollbar (spans under both tree and vertical scrollbar)
    hs = ttk.Scrollbar(tv_frame, orient='horizontal', command=tv.xview)
    hs.grid(row=1, column=0, columnspan=2, sticky='ew')

    tv.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)

    df_subset = df_subset.fillna('')
    tv['columns'] = list(df_subset.columns)
    for col in df_subset.columns:
        tv.heading(col, text=col)
        tv.column(col, width=100, anchor='w')
    for row in df_subset.to_numpy().tolist():
        tv.insert("", "end", values=row)

def draw_histogram(df, subject_name):
    # creates and returns a matplotlib Figure for the histogram
    fig = plt.figure(figsize=(6, 4))
    if subject_name in df.columns:
        scores = pd.to_numeric(df[subject_name], errors='coerce').dropna()
        plt.hist(scores, bins=10, range=(0, 100), color='#5DADE2', edgecolor='slategrey')
        plt.title(f"Grade Distribution: {subject_name}")
        plt.xlabel("Score")
        plt.ylabel("Number of Students")
    else:
        plt.text(0.5, 0.5, "Subject Not Found", ha='center')
    plt.tight_layout()
    return fig

def draw_top_bottom(df):
    # safer Figure/Axes-based implementation and fallback for name column
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    temp_df = df.copy()
    temp_df['Average'] = temp_df[numeric_cols].mean(axis=1)
    temp_df = temp_df.sort_values('Average')
    combined = pd.concat([temp_df.head(5), temp_df.tail(5)])

    # choose a name column (fallback to index if none)
    if 'student name' in combined.columns:
        name_col = 'student name'
    else:
        name_col = combined.columns[0] if len(combined.columns) > 0 else None

    colors = ['#B0B3B8'] * min(5, len(combined)) + ['#5DADE2'] * max(0, len(combined) - 5)

    fig = Figure(figsize=(8, 6), dpi=100)
    ax = fig.add_subplot(111)
    labels = combined[name_col].astype(str) if name_col is not None else combined.index.astype(str)
    ax.barh(labels, combined['Average'], color=colors, edgecolor='slategrey')
    ax.set_title("Top 5 vs Bottom 5 Students")
    ax.set_xlabel("Overall Average Score")
    ax.invert_yaxis()  # show highest at top
    fig.tight_layout()
    return fig

def display_figure(fig_to_show):
    global canvas
    clear_content_frame()
    canvas = FigureCanvasTkAgg(fig_to_show, master=content_frame)
    canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    canvas.draw()
    content_frame.update_idletasks()

def update_graph(subject):
    if subject == "" or subject is None:
        subject = subjects[0]
    fig_hist = draw_histogram(df, subject)
    display_figure(fig_hist)

# buttons to show top/worst students in place of the graph + restore graph
def show_top():
    display_table(top_students, "Top Students")

def show_worst():
    display_table(lowest_students, "Lowest Performing Students")

def restore_graph():
    global view_mode
    view_mode = 'hist'
    display_graph()
    update_graph(subject_var.get())

# place two new buttons to the left of the combobox (next to existing temp buttons)
btn_top = ttk.Button(buttons_frame, text="Top Students", command=show_top)
btn_top.grid(row=0, column=0, padx=(0,6))
btn_worst = ttk.Button(buttons_frame, text="Worst Students", command=show_worst)
btn_worst.grid(row=0, column=1, padx=(0,6))
# shift existing label/combobox one column to the right if needed
tk.Label(buttons_frame, text="Subject:", bg='#3E3E3E', fg='white').grid(row=0, column=2, sticky='w')
subject_var = tk.StringVar()
combo = ttk.Combobox(buttons_frame, textvariable=subject_var, values=subjects, state='readonly', width=12)
combo.grid(row=0, column=3, sticky='w', padx=(8,0))
combo.set(subjects[0])

# add small "Show Graph" button to restore graph view
btn_restore = ttk.Button(buttons_frame, text="Show Graph", command=restore_graph)
btn_restore.grid(row=0, column=4, padx=(8,0))

def show_pass_fail_pie():
    global canvas, view_mode
    view_mode = 'pie'
    clear_content_frame()
    subject = subject_var.get() or subjects[0]
    threshold = 50

    # use selected subject if present, otherwise compute per-row average from subject columns
    if subject in df.columns:
        series = pd.to_numeric(df[subject], errors='coerce').dropna()
    else:
        series = pd.to_numeric(df[subjects].mean(axis=1), errors='coerce').dropna()

    passed = int((series >= threshold).sum())
    failed = int((series < threshold).sum())

    # build pie safely if no data
    total = passed + failed
    if total == 0:
        labels = ['No data']
        sizes = [1]
        colors = ['#95A5A6']
        autopct = None
    else:
        labels = ['Pass', 'Fail']
        sizes = [passed, failed]
        colors = ['#5DADE2', '#E74C3C']
        autopct = '%1.1f%%'

    fig_pie = Figure(figsize=(6, 4), dpi=100)
    ax_pie = fig_pie.add_subplot(111)
    ax_pie.pie(sizes, labels=labels, colors=colors, autopct=autopct, startangle=90)
    ax_pie.axis('equal')
    ax_pie.set_title(f'Pass/Fail ({subject})')

    canvas = FigureCanvasTkAgg(fig_pie, master=content_frame)
    canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    canvas.draw()

btn_pie = ttk.Button(buttons_frame, text="Pass/Fail Pie", command=show_pass_fail_pie)
btn_pie.grid(row=0, column=5, padx=(8,0))

def draw_comparison(df):
    # returns a Figure comparing average score per subject
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)

    # use the predefined subjects list (skip non-existing)
    subs = [s for s in subjects if s in df.columns]
    averages = [df[s].dropna().astype(float).mean() if s in df.columns else 0 for s in subs]

    my_colors = ['salmon' if (a < 50 or np.isnan(a)) else 'lightgreen' for a in averages]
    bars = ax.bar(subs, averages, color=my_colors, edgecolor='black')

    for bar, height in zip(bars, averages):
        h = 0 if np.isnan(height) else height
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1, f'{h:.1f}', ha='center', va='bottom')

    ax.set_title("Average Score by Subject")
    ax.set_ylabel("Average Score")
    ax.set_ylim(0, 100)
    fig.tight_layout()
    return fig

def show_comparison():
    global canvas, view_mode
    view_mode = 'comparison'
    display_figure(draw_comparison(df))

btn_compare = ttk.Button(buttons_frame, text="Compare Subjects", command=show_comparison)
btn_compare.grid(row=0, column=7, padx=(8,0))

def show_top_bottom():
    global canvas, view_mode
    view_mode = 'topbottom'
    display_figure(draw_top_bottom(df))

btn_topbottom = ttk.Button(buttons_frame, text="Top/Bottom 5", command=show_top_bottom)
btn_topbottom.grid(row=0, column=6, padx=(8,0))

# initial display is the graph
display_figure(draw_histogram(df, subjects[0]))

# update when dropdown changes: show graph + redraw
def on_subject_change(event):
    # update current view for selected subject
    if view_mode == 'pie':
        show_pass_fail_pie()
    elif view_mode == 'topbottom':
        show_top_bottom()
    elif view_mode == 'comparison':
        show_comparison()
    else:
        update_graph(subject_var.get())

combo.bind("<<ComboboxSelected>>", on_subject_change)

#For loop to convert all the data to numeric
for col in subjects:
    df[col] = pd.to_numeric(df[col], errors='coerce')
#Add Total column
df['Total']= df[subjects].sum(axis=1)
#Add Average column
df['Average'] = df[subjects].mean(axis=1)
#Add top students part
top_students = df.sort_values(by='Total', ascending=False).head()
print("Top 5 Students:")
print(top_students)
#Add lowest students part
lowest_students = df.sort_values(by='Total', ascending=True).head()
print("Students that needs attention: ")
print(lowest_students)
#Add the status column pass/fail, "lambda x" creates anonymous function where x represents each individual average score
pass_students = 50
df['Status'] = df['Average'].apply(lambda x: 'Pass' if x >= pass_students else 'Fail')
total_students=len(df)
passed=(df['Average']>=pass_students).sum()
failed=(df['Average']<pass_students).sum()
#pass and fail mathematical calculation
pass_percentage=(passed/total_students)*100
fail_percentage=(failed/total_students)*100
print("\npass percentage by average: ")
print(f'passed: {passed}({pass_percentage:.2f}%)')
print(f'Failed: {failed}({fail_percentage:.2f}%)')
print("\n"+"-"*46)
print("pass and fail in each course:")
print("-"*46)
#for loop to add the pass/fail percentage in every course
for subject in subjects:
    subject_pass=(df[subject]>=pass_percentage).sum()
    subject_fail=(df[subject]<pass_percentage).sum()
    subject_pass_percentage=(subject_pass/total_students)*100
    subject_fail_percentage=(subject_fail/total_students)*100
    print(f"\n{subject}:")
    print(f"pass: {subject_pass} students ({subject_pass_percentage:.2f}%)")
    print(f"fail: {subject_fail} students ({subject_fail_percentage:.2f}%)")
#GPA calculation
def GPA(Average):
    if Average >=93:
        return 4.0
    elif Average >=90:
        return 3.7
    elif Average >=85:
        return 3.5
    elif Average >=83:
        return 3.3
    elif Average >=80:
        return 3.0
    elif Average >=75:
        return 2.7
    elif Average >=70:
        return 2.5
    elif Average >=60:
        return 2.2
    elif Average >=50:
        return 2.0
    else:
        return 0.0
#Add gpa column
df['GPA']=df['Average'].apply(GPA)
#To print all the columns together and it can be removed if other team members want
pd.set_option('display.max_columns',None)
def search(df,name):
    #str to read line as string (case=False):to ignore Upper and lower letter(insenstive) and (na=False):To not crash if name is missing
    result = df[df['student name'].str.contains(name, case=False,na=False)]
    #if condition to decide whether the name is in the database or no
    if result.empty:
        print(f"\nNo student called '{name}'")
    else:
        print(f"\nResults for '{name}':")
        print(result)
    return result

######

#creates table
frame = tk.Frame(root, bg='#3E3E3E')
# make the table frame span both rows so it fills full vertical space
frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)
 
tree = ttk.Treeview(frame, show="headings")  # let geometry control height
tree.grid(row=0, column=0,sticky="nsew")
scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
scroll.grid(row=0, column=1, sticky='ns')
tree.configure(yscrollcommand=scroll.set)
#البلح مفيد

df = df.fillna("") #fills empty
tree["columns"] = list(df.columns)
df.columns = df.columns.str.strip()

for col in df.columns: #adds columns to table
        tree.heading(col, text=col)
        tree.column(col, width=78)

for row in df.to_numpy().tolist(): #adds data 
        tree.insert("", "end", values=row) 




root.mainloop()
