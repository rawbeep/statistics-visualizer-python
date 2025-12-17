import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys

try:
    import pandas as pd
    import numpy as np
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Missing Dependencies", 
                        "Please install: pip install pandas numpy openpyxl matplotlib")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from datetime import datetime

class GradebookViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Gradebook Viewer Pro")
        self.root.geometry("1600x900")
        self.root.configure(bg="#ecf0f1")
        
        self.df = None
        self.numeric_cols = []
        self.filtered_df = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Top toolbar
        toolbar = tk.Frame(self.root, bg="#2c3e50", height=80)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        tk.Label(toolbar, text="📚 Gradebook Viewer Pro", 
                font=("Arial", 22, "bold"), bg="#2c3e50", fg="white").pack(side=tk.LEFT, padx=25, pady=20)
        
        btn_frame = tk.Frame(toolbar, bg="#2c3e50")
        btn_frame.pack(side=tk.RIGHT, padx=25)
        
        tk.Button(btn_frame, text="📁 Load File", command=self.load_file,
                 font=("Arial", 11, "bold"), bg="#3498db", fg="white",
                 padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="💾 Export", command=self.export_statistics,
                 font=("Arial", 11, "bold"), bg="#27ae60", fg="white",
                 padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_all,
                 font=("Arial", 11, "bold"), bg="#9b59b6", fg="white",
                 padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Search bar
        search_frame = tk.Frame(self.root, bg="white", relief=tk.RIDGE, bd=1)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="🔍", font=("Arial", 14), bg="white").pack(side=tk.LEFT, padx=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_data)
        tk.Entry(search_frame, textvariable=self.search_var, 
                font=("Arial", 11), width=40).pack(side=tk.LEFT, padx=5, pady=8)
        
        tk.Button(search_frame, text="Clear", command=lambda: self.search_var.set(""),
                 bg="#95a5a6", fg="white", padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Main content
        content = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5, bg="#bdc3c7")
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left: Data table
        left = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=2)
        content.add(left, minsize=700)
        
        tk.Label(left, text="📋 Student Data", font=("Arial", 14, "bold"),
                bg="#34495e", fg="white", pady=12).pack(fill=tk.X)
        
        tree_frame = tk.Frame(left)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scroll_y = ttk.Scrollbar(tree_frame)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scroll_y.set,
                                xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Right: Statistics
        right = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=2)
        content.add(right, minsize=600)
        
        tk.Label(right, text="📊 Statistics & Analysis", font=("Arial", 14, "bold"),
                bg="#34495e", fg="white", pady=12).pack(fill=tk.X)
        
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Tab 1: Overview
        self.overview_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.overview_tab, text="📈 Overview")
        
        self.overview_text = scrolledtext.ScrolledText(self.overview_tab, 
                                                       wrap=tk.WORD, 
                                                       font=("Consolas", 10),
                                                       bg="#f8f9fa", padx=15, pady=15)
        self.overview_text.pack(fill=tk.BOTH, expand=True)
        
        # Tab 2: Assignments
        self.assign_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.assign_tab, text="📝 Assignments")
        
        self.assign_text = scrolledtext.ScrolledText(self.assign_tab, 
                                                     wrap=tk.WORD,
                                                     font=("Consolas", 9),
                                                     bg="#f8f9fa", padx=15, pady=15)
        self.assign_text.pack(fill=tk.BOTH, expand=True)
        
        # Tab 3: Rankings
        self.rank_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.rank_tab, text="🏆 Rankings")
        
        rank_container = tk.Frame(self.rank_tab, bg="white")
        rank_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        top_frame = tk.LabelFrame(rank_container, text="🥇 Top Performers",
                                 font=("Arial", 11, "bold"), bg="white", fg="#27ae60")
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.top_text = scrolledtext.ScrolledText(top_frame, wrap=tk.WORD,
                                                  font=("Consolas", 10), bg="#f8f9fa",
                                                  height=13)
        self.top_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        bottom_frame = tk.LabelFrame(rank_container, text="⚠️ Needs Attention",
                                     font=("Arial", 11, "bold"), bg="white", fg="#e74c3c")
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        self.bottom_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD,
                                                     font=("Consolas", 10), bg="#f8f9fa",
                                                     height=13)
        self.bottom_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if HAS_MATPLOTLIB:
            # Tab 4: Charts
            self.chart_tab = tk.Frame(self.notebook, bg="white")
            self.notebook.add(self.chart_tab, text="📊 Charts")
            
            chart_controls = tk.Frame(self.chart_tab, bg="white")
            chart_controls.pack(fill=tk.X, padx=15, pady=12)
            
            tk.Label(chart_controls, text="Select:", font=("Arial", 11, "bold"),
                    bg="white").pack(side=tk.LEFT, padx=5)
            
            self.chart_var = tk.StringVar()
            self.chart_combo = ttk.Combobox(chart_controls, textvariable=self.chart_var,
                                           state="readonly", width=25)
            self.chart_combo.pack(side=tk.LEFT, padx=5)
            self.chart_combo.bind("<<ComboboxSelected>>", self.update_chart)
            
            self.chart_frame = tk.Frame(self.chart_tab, bg="white")
            self.chart_frame.pack(fill=tk.BOTH, expand=True)
            
            # Tab 5: Comparison
            self.comp_tab = tk.Frame(self.notebook, bg="white")
            self.notebook.add(self.comp_tab, text="📉 Compare")
            
            self.comp_frame = tk.Frame(self.comp_tab, bg="white")
            self.comp_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        status = tk.Frame(self.root, bg="#34495e", height=30)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        status.pack_propagate(False)
        
        self.status_label = tk.Label(status, text="Ready", bg="#34495e",
                                     fg="#2ecc71", font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=15, pady=5)
        
        self.record_label = tk.Label(status, text="", bg="#34495e",
                                     fg="#ecf0f1", font=("Arial", 10))
        self.record_label.pack(side=tk.RIGHT, padx=15, pady=5)
    
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("Excel/CSV", "*.xlsx *.xls *.csv"), ("All", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.status_label.config(text="Loading...", fg="#f39c12")
            self.root.update()
            
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)
            
            self.filtered_df = self.df.copy()
            self.process_data()
            self.display_data()
            self.refresh_all()
            
            self.status_label.config(text=f"✓ Loaded: {file_path.split('/')[-1]}", fg="#2ecc71")
            
            messagebox.showinfo("Success", 
                              f"File loaded!\n\n"
                              f"Students: {len(self.df)}\n"
                              f"Columns: {len(self.df.columns)}\n"
                              f"Grades: {len(self.numeric_cols)}")
        except Exception as e:
            msg = f"Load failed:\n{str(e)}"
            if "openpyxl" in str(e):
                msg += "\n\nInstall: pip install openpyxl"
            messagebox.showerror("Error", msg)
            self.status_label.config(text="✖ Load failed", fg="#e74c3c")
    
    def process_data(self):
        self.numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if HAS_MATPLOTLIB and self.numeric_cols:
            self.chart_combo['values'] = self.numeric_cols
            self.chart_combo.current(0)
    
    def display_data(self, df=None):
        if df is None:
            df = self.filtered_df if self.filtered_df is not None else self.df
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if df is None or len(df) == 0:
            return
        
        self.tree['columns'] = list(df.columns)
        self.tree['show'] = 'headings'
        
        for col in df.columns:
            self.tree.heading(col, text=col)
            width = 150 if col in self.numeric_cols else 180
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        for idx, row in df.iterrows():
            values = []
            for col in df.columns:
                val = row[col]
                if pd.isna(val):
                    values.append("")
                elif col in self.numeric_cols:
                    values.append(f"{val:.1f}")
                else:
                    values.append(str(val))
            
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.tree.insert('', tk.END, values=values, tags=(tag,))
        
        self.tree.tag_configure('even', background='#f8f9fa')
        self.tree.tag_configure('odd', background='white')
        
        self.record_label.config(text=f"Showing {len(df)} of {len(self.df)} records")
    
    def filter_data(self, *args):
        if self.df is None:
            return
        
        search = self.search_var.get().lower().strip()
        
        if not search:
            self.filtered_df = self.df.copy()
        else:
            mask = self.df.astype(str).apply(
                lambda x: x.str.lower().str.contains(search, na=False)
            ).any(axis=1)
            self.filtered_df = self.df[mask]
        
        self.display_data()
    
    def refresh_all(self):
        if self.df is None:
            return
        
        try:
            self.calc_overview()
            self.calc_assignments()
            self.calc_rankings()
            
            if HAS_MATPLOTLIB:
                self.update_chart()
                self.update_comparison()
            
            self.status_label.config(text="✓ Refreshed", fg="#2ecc71")
        except Exception as e:
            messagebox.showerror("Error", f"Refresh failed:\n{str(e)}")
    
    def calc_overview(self):
        self.overview_text.delete(1.0, tk.END)
        
        if not self.numeric_cols:
            self.overview_text.insert(tk.END, "\nNo grade data found.\n")
            return
        
        out = "\n" + "="*60 + "\n"
        out += "          GRADEBOOK OVERVIEW\n"
        out += "="*60 + "\n\n"
        out += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        out += f"👥 Students: {len(self.df)}\n"
        out += f"📝 Assignments: {len(self.numeric_cols)}\n\n"
        
        all_grades = self.df[self.numeric_cols].values.flatten()
        all_grades = all_grades[~np.isnan(all_grades)]
        
        out += "─"*60 + "\n"
        out += "📊 OVERALL PERFORMANCE\n"
        out += "─"*60 + "\n"
        out += f"Total Submissions: {len(all_grades)}\n"
        out += f"Class Average: {all_grades.mean():.2f}%\n"
        out += f"Median: {np.median(all_grades):.2f}%\n"
        out += f"Std Dev: {all_grades.std():.2f}\n"
        out += f"Range: {all_grades.min():.2f} - {all_grades.max():.2f}\n\n"
        
        a = np.sum(all_grades >= 90)
        b = np.sum((all_grades >= 80) & (all_grades < 90))
        c = np.sum((all_grades >= 70) & (all_grades < 80))
        d = np.sum((all_grades >= 60) & (all_grades < 70))
        f = np.sum(all_grades < 60)
        total = len(all_grades)
        
        out += "📈 GRADE DISTRIBUTION\n"
        out += "─"*60 + "\n"
        out += f"A: {a:4d} ({a/total*100:5.1f}%) {'█'*min(int(a/total*30),30)}\n"
        out += f"B: {b:4d} ({b/total*100:5.1f}%) {'█'*min(int(b/total*30),30)}\n"
        out += f"C: {c:4d} ({c/total*100:5.1f}%) {'█'*min(int(c/total*30),30)}\n"
        out += f"D: {d:4d} ({d/total*100:5.1f}%) {'█'*min(int(d/total*30),30)}\n"
        out += f"F: {f:4d} ({f/total*100:5.1f}%) {'█'*min(int(f/total*30),30)}\n\n"
        
        pass_rate = (total - f) / total * 100
        out += f"✓ Pass Rate: {pass_rate:.1f}%\n\n"
        
        avgs = self.df[self.numeric_cols].mean(axis=1)
        out += "─"*60 + "\n"
        out += "👥 STUDENT SUMMARY\n"
        out += "─"*60 + "\n"
        out += f"Average Score: {avgs.mean():.2f}%\n"
        out += f"Median: {avgs.median():.2f}%\n"
        out += f"Range: {avgs.min():.2f} - {avgs.max():.2f}%\n\n"
        
        at_risk = np.sum(avgs < 60)
        if at_risk > 0:
            out += f"⚠️  At Risk (<60%): {at_risk} ({at_risk/len(avgs)*100:.1f}%)\n\n"
        
        out += "="*60 + "\n"
        self.overview_text.insert(tk.END, out)
    
    def calc_assignments(self):
        self.assign_text.delete(1.0, tk.END)
        
        if not self.numeric_cols:
            return
        
        out = "\n" + "="*65 + "\n"
        out += "          ASSIGNMENT STATISTICS\n"
        out += "="*65 + "\n\n"
        
        for i, col in enumerate(self.numeric_cols, 1):
            data = self.df[col].dropna()
            if len(data) == 0:
                continue
            
            out += f"\n{'━'*65}\n"
            out += f"#{i}: {col}\n"
            out += f"{'━'*65}\n"
            out += f"Submissions: {len(data)}/{len(self.df)} ({len(data)/len(self.df)*100:.0f}%)\n"
            out += f"Mean:     {data.mean():.2f}\n"
            out += f"Median:   {data.median():.2f}\n"
            out += f"Std Dev:  {data.std():.2f}\n"
            out += f"Range:    {data.min():.2f} - {data.max():.2f}\n\n"
            
            q1, q3 = data.quantile([0.25, 0.75])
            out += f"Q1: {q1:.2f}  |  Q3: {q3:.2f}  |  IQR: {q3-q1:.2f}\n\n"
            
            if data.max() <= 100:
                a = len(data[data >= 90])
                b = len(data[(data >= 80) & (data < 90)])
                c = len(data[(data >= 70) & (data < 80)])
                d = len(data[(data >= 60) & (data < 70)])
                f = len(data[data < 60])
                
                out += "Grades:\n"
                out += f" A: {a:3d} ({a/len(data)*100:5.1f}%) {'█'*int(a/len(data)*20)}\n"
                out += f" B: {b:3d} ({b/len(data)*100:5.1f}%) {'█'*int(b/len(data)*20)}\n"
                out += f" C: {c:3d} ({c/len(data)*100:5.1f}%) {'█'*int(c/len(data)*20)}\n"
                out += f" D: {d:3d} ({d/len(data)*100:5.1f}%) {'█'*int(d/len(data)*20)}\n"
                out += f" F: {f:3d} ({f/len(data)*100:5.1f}%) {'█'*int(f/len(data)*20)}\n\n"
                out += f"Pass Rate: {(len(data)-f)/len(data)*100:.1f}%\n"
        
        out += "\n" + "="*65 + "\n"
        self.assign_text.insert(tk.END, out)
    
    def calc_rankings(self):
        self.top_text.delete(1.0, tk.END)
        self.bottom_text.delete(1.0, tk.END)
        
        if not self.numeric_cols:
            return
        
        avgs = self.df[self.numeric_cols].mean(axis=1)
        self.df['_avg_'] = avgs
        sorted_df = self.df.sort_values('_avg_', ascending=False)
        
        # Top performers
        top_out = "\n"
        for rank, (idx, row) in enumerate(sorted_df.head(10).iterrows(), 1):
            name = str(row.iloc[0]) if len(row) > 0 else f"Student {idx}"
            avg = row['_avg_']
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank:2d}."
            top_out += f"{medal} {name[:30]:30s} {avg:6.2f}%\n"
            grades = [f"{row[c]:.1f}" for c in self.numeric_cols if not pd.isna(row[c])]
            top_out += f"    {', '.join(grades[:10])}\n\n"
        
        self.top_text.insert(tk.END, top_out)
        
        # Bottom performers
        bottom_out = "\n"
        for idx, row in sorted_df.tail(10)[::-1].iterrows():
            name = str(row.iloc[0]) if len(row) > 0 else f"Student {idx}"
            avg = row['_avg_']
            bottom_out += f"⚠️  {name[:30]:30s} {avg:6.2f}%\n"
            grades = " ".join([f"[{row[c]:.1f}]" if row[c] < 60 else f"{row[c]:.1f}"
                              for c in self.numeric_cols if not pd.isna(row[c])])
            bottom_out += f"    {grades}\n\n"
        
        self.bottom_text.insert(tk.END, bottom_out)
        
        self.df.drop('_avg_', axis=1, inplace=True)
    
    def update_chart(self, event=None):
        if not HAS_MATPLOTLIB or not self.numeric_cols:
            return
        
        for w in self.chart_frame.winfo_children():
            w.destroy()
        
        col = self.chart_var.get()
        if not col:
            return
        
        data = self.df[col].dropna()
        
        fig = Figure(figsize=(6, 4.5), dpi=100)
        ax = fig.add_subplot(111)
        
        n, bins, patches = ax.hist(data, bins=min(20, len(data)//3),
                                    alpha=0.75, edgecolor='black', linewidth=1.2)
        
        if data.max() <= 100:
            for i, patch in enumerate(patches):
                if bins[i] >= 90:
                    patch.set_facecolor('#2ecc71')
                elif bins[i] >= 80:
                    patch.set_facecolor('#3498db')
                elif bins[i] >= 70:
                    patch.set_facecolor('#f39c12')
                elif bins[i] >= 60:
                    patch.set_facecolor('#e67e22')
                else:
                    patch.set_facecolor('#e74c3c')
        
        mean = data.mean()
        median = data.median()
        
        ax.axvline(mean, color='red', linestyle='--', linewidth=2.5,
                  label=f'Mean: {mean:.2f}', alpha=0.8)
        ax.axvline(median, color='green', linestyle='--', linewidth=2.5,
                  label=f'Median: {median:.2f}', alpha=0.8)
        
        ax.set_xlabel('Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title(f'{col} Distribution', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_comparison(self):
        if not HAS_MATPLOTLIB or not self.numeric_cols:
            return
        
        for w in self.comp_frame.winfo_children():
            w.destroy()
        
        fig = Figure(figsize=(6, 4.5), dpi=100)
        ax = fig.add_subplot(111)
        
        means = [self.df[c].mean() for c in self.numeric_cols]
        x = np.arange(len(self.numeric_cols))
        
        bars = ax.bar(x, means, color='#3498db', alpha=0.8, edgecolor='black')
        
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h,
                   f'{h:.1f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Average Score', fontsize=12, fontweight='bold')
        ax.set_title('Assignment Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([c[:10]+'...' if len(c)>10 else c
                           for c in self.numeric_cols], rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.comp_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def export_statistics(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Load a file first!")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All", "*.*")]
        )
        
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.overview_text.get(1.0, tk.END))
                    f.write("\n\n" + "="*80 + "\n\n")
                    f.write(self.assign_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Exported to:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GradebookViewer(root)
    root.mainloop()
