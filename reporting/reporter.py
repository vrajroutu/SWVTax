import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from loguru import logger

class Reporter:
    def __init__(self, config):
        self.config = config
        self.output_dir = os.path.join('reporting', 'output')
        os.makedirs(self.output_dir, exist_ok=True)

    def line_chart(self, df, x, y, hue=None, title='', filename='line_chart.png'):
        if df is None or df.empty:
            logger.warning(f"Cannot create line chart: DataFrame is empty or None")
            return
        plt.figure(figsize=(10,6))
        sns.lineplot(data=df, x=x, y=y, hue=hue)
        plt.title(title)
        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path)
        plt.close()
        logger.info(f"Saved chart: {path}")

    def summary_table(self, df, filename='summary.csv'):
        if df is None or df.empty:
            logger.warning(f"Cannot save summary table: DataFrame is empty or None")
            return
        path = os.path.join(self.output_dir, filename)
        df.to_csv(path, index=False)
        logger.info(f"Saved summary table: {path}")

    def to_excel(self, df, filename='summary.xlsx'):
        if df is None or df.empty:
            logger.warning(f"Cannot save Excel file: DataFrame is empty or None")
            return
        path = os.path.join(self.output_dir, filename)
        df.to_excel(path, index=False)
        logger.info(f"Saved Excel file: {path}")

    def to_pdf(self, df, filename='summary.pdf'):
        try:
            # Check if DataFrame is empty before processing
            if df is None or df.empty:
                logger.warning(f"Cannot save PDF: DataFrame is empty or None")
                return

            import matplotlib.backends.backend_pdf
            pdf_path = os.path.join(self.output_dir, filename)
            pdf = matplotlib.backends.backend_pdf.PdfPages(pdf_path)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.axis('tight')
            ax.axis('off')
            table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
            pdf.savefig(fig, bbox_inches='tight')
            pdf.close()
            plt.close(fig)
            logger.info(f"Saved PDF: {pdf_path}")
        except Exception as e:
            logger.error(f"Failed to save PDF: {e}")

    def compare_new_vs_old_chart(self, df, title='Tax Comparison: New vs. Old Homes', filename='tax_comparison_new_vs_old.png'):
        plt.figure(figsize=(10,6))
        sns.lineplot(data=df, x='year', y='tax', hue='home_type', marker='o')
        plt.title(title)
        plt.ylabel('Average Property Tax')
        plt.xlabel('Year')
        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path)
        plt.close()
        logger.info(f"Saved new vs. old home comparison chart: {path}")

    def compare_new_vs_old_table(self, df, filename='tax_comparison_new_vs_old.csv'):
        path = os.path.join(self.output_dir, filename)
        df.to_csv(path, index=False)
        logger.info(f"Saved new vs. old home comparison table: {path}")

    def generate_case_report(self, executive_summary, findings, tables, charts, filename='case_report.pdf'):
        from matplotlib.backends.backend_pdf import PdfPages
        from fpdf import FPDF
        pdf_path = os.path.join(self.output_dir, filename)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Roxbury Township Property Tax Analysis Report', ln=True, align='C')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)
        pdf.multi_cell(0, 10, executive_summary)
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Key Findings', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, findings)
        pdf.ln(5)
        for table_title, df in tables.items():
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, table_title, ln=True)
            pdf.set_font('Arial', '', 10)
            table_str = df.to_string(index=False)
            pdf.multi_cell(0, 6, table_str)
            pdf.ln(2)
        for chart_path in charts:
            pdf.add_page()
            pdf.image(chart_path, x=10, y=20, w=180)
        pdf.output(pdf_path)
        logger.info(f"Saved detailed case report: {pdf_path}")
