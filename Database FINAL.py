import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
#reading the file
df = pd.read_csv(r'C:\Users\anase\Desktop\Project files\project.csv')
subjects = ['CS101','CS102','ENG102','MATH','SSC1']
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
pass_students = 50
#Add the status column pass/fail, "lambda x" creates anonymous function where x represents each individual average score
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

#Search part
#new function called search allows user to search
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


print("\n" + "=" * 50)
student_name = input("Enter student name to search: ")
#function call
search(df, student_name)


print(df)
































