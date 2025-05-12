"""Reporting module for trades."""

import os
import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
import pdfkit


def generate_pair_report(
    df_matches: pd.DataFrame,
    login_a: int,
    login_b: int,
    output_dir: str = "reports",
    template_dir: str = "templates",
    template_file: str = "report_template.html",
    generate_pdf: bool = True,
) -> None:
    """
    Generate an HTML and optional PDF report for a matched trading account pair.

    Parameters:
    - df_matches: DataFrame with all matched trades.
    - login_a: First trading account login.
    - login_b: Second trading account login.
    - output_dir: Path to save the report.
    - template_dir: Folder containing Jinja2 HTML templates.
    - template_file: HTML template filename.
    - generate_pdf: Whether to export a PDF copy.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Filter matches involving the account pair (in either direction)
    filtered_df = df_matches[
        ((df_matches["trading_account_login_a"] == login_a) & (df_matches["trading_account_login_b"] == login_b)) |
        ((df_matches["trading_account_login_a"] == login_b) & (df_matches["trading_account_login_b"] == login_a))
    ]

    if filtered_df.empty:
        print(f"[WARN] No matches found between accounts {login_a} and {login_b}.")
        return

    # Generate pie chart for category distribution
    pie_chart_filename = f"pie_{login_a}_{login_b}.png"
    pie_chart_path = os.path.join(output_dir, pie_chart_filename)
    filtered_df["category"].value_counts().plot.pie(
        autopct="%1.1f%%",
        figsize=(5, 5),
        title="Match Category Distribution"
    )
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(pie_chart_path)
    plt.close()

    # Prepare HTML via Jinja2
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    rendered_html = template.render(
        top_pair=(login_a, login_b),
        top_count=len(filtered_df),
        pie_chart_path=pie_chart_filename,
        table_html=filtered_df.to_html(index=False, classes="table table-sm table-striped")
    )

    # Save HTML
    html_path = os.path.join(output_dir, f"report_{login_a}_{login_b}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)
    print(f"[INFO] HTML report saved: {html_path}")

    # convert to PDF
    if generate_pdf:
        try:
            pdf_path = html_path.replace(".html", ".pdf")
            pdfkit.from_file(html_path, pdf_path)
            print(f"[INFO] PDF report saved: {pdf_path}")
        except Exception as e:
            print(f"[ERROR] Failed to generate PDF: {e}")
