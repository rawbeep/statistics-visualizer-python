import pandas as pd
df = pd.read_csv(r'project.csv')
subjects = ['CS101','CS102','ENG102','MATH','SSC1']
for col in subjects:
    df[col] = pd.to_numeric(df[col], errors='coerce')
    df['Total']= df[subjects].sum(axis=1)
df['Average'] = df[subjects].mean(axis=1)
top_students = df.sort_values(by='Total', ascending=False).head()
print("Top 5 Students:")
print(top_students)
lowest_students = df.sort_values(by='Total', ascending=True).head()
print("Students that needs attention: ")
print(lowest_students)
print(df)
