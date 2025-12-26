import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_csv("project.csv")


grades = [100,90,70, 50, 40, 25,0]
cumulative_counts = {}
for grade in grades:
    count = len(df[df['SSC1'] >= grade])
    cumulative_counts[f'{grade}+'] = count


plt.figure(figsize=(10, 6))
categories = list(cumulative_counts.keys())
counts = list(cumulative_counts.values())



plt.bar(categories, counts, align='center', color="blue", edgecolor='red', linewidth=3)
plt.xticks(categories, categories, rotation=90)
plt.xlabel('Grade Threshold', fontsize=12, fontweight='bold')
plt.ylabel('Number of Students', fontsize=12, fontweight='bold')
plt.title('Cumulative Student Grade Distribution (CS102)', fontsize=14)
plt.tight_layout()
plt.show()


