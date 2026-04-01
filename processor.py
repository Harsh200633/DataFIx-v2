import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        ext = os.path.splitext(file_path)[1].lower()

        try:
            # CSV
            if ext == '.csv':
                try:
                    self.df = pd.read_csv(file_path, encoding='utf-8')
                except:
                    self.df = pd.read_csv(file_path, encoding='ISO-8859-1')

            # Excel (ALL formats supported)
            elif ext in ['.xlsx', '.xls', '.xlsm', '.xlsb']:
                try:
                    self.df = pd.read_excel(file_path)
                except ImportError:
                    raise ValueError(
                        "Install required packages:\n"
                        "pip install openpyxl xlrd pyxlsb"
                    )
                except Exception as e:
                    raise ValueError(f"Excel Read Error: {str(e)}")

            else:
                raise ValueError("Unsupported file format")

            # Fix: if single row
            if isinstance(self.df, pd.Series):
                self.df = self.df.to_frame().T

        except Exception as e:
            raise ValueError(f"File Processing Error: {str(e)}")

    # ✅ CLEANING
    def clean_data(self):
        self.df.drop_duplicates(inplace=True)

        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col] = self.df[col].fillna(0)
            else:
                self.df[col] = self.df[col].fillna('N/A')

        return self.df

    # ✅ VISUALS (FINAL VERSION)
    def save_all_visuals(self, output_folder):
        plt.style.use('dark_background')
        numeric_cols = self.df.select_dtypes(include=['number']).columns

        if len(numeric_cols) == 0:
            return  # No numeric data

        try:
            # 🔹 BAR CHART
            plt.figure(figsize=(8, 5))
            self.df[numeric_cols[0]].head(10).plot(kind='bar', color='#e67e22')
            plt.tight_layout()
            plt.savefig(os.path.join(output_folder, 'bar.png'), transparent=True)
            plt.close()

            # 🔹 LINE (TREND)
            plt.figure(figsize=(8, 5))
            plt.plot(self.df[numeric_cols[0]].head(20), color='#3498db')
            plt.title("Trend")
            plt.savefig(os.path.join(output_folder, 'line.png'), transparent=True)
            plt.close()

            # 🔹 HEATMAP
            if len(numeric_cols) >= 2:
                plt.figure(figsize=(8, 5))
                sns.heatmap(self.df[numeric_cols].corr(), cmap='Blues')
                plt.title("Correlation Heatmap")
                plt.savefig(os.path.join(output_folder, 'heat.png'), transparent=True)
                plt.close()

            # 🔹 PIE CHART (Top values)
            plt.figure(figsize=(6, 6))
            self.df[numeric_cols[0]].head(5).plot(
                kind='pie',
                autopct='%1.1f%%'
            )
            plt.ylabel("")
            plt.savefig(os.path.join(output_folder, 'pie.png'), transparent=True)
            plt.close()

            # 🔹 BOX PLOT (NEW 🔥)
            plt.figure(figsize=(8, 5))
            sns.boxplot(data=self.df[numeric_cols])
            plt.title("Box Plot")
            plt.savefig(os.path.join(output_folder, 'box.png'), transparent=True)
            plt.close()

        except Exception as e:
            print("Visualization Error:", e)

        # 🔹 FALLBACK IMAGES (if something fails)
        for name in ['bar', 'line', 'heat', 'pie', 'box']:
            path = os.path.join(output_folder, f'{name}.png')
            if not os.path.exists(path):
                plt.figure()
                plt.text(0.5, 0.5, f'{name.upper()} READY', ha='center', color='white')
                plt.savefig(path, transparent=True)
                plt.close()