import re
import pandas as pd
import pypandoc

import params


def parse_file(filename: str):
    rows = [] 
    with open(filename, "r", encoding="utf-8") as f:
        entries = f.readlines()
    sanitized_entries = []
    for entry in entries:
        if ":" in entry:
            sanitized_entries.append(entry)
    entries = sanitized_entries
    message_pattern = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}) - ([^:]+): (.*)$")

    for entry in entries:
        m = message_pattern.match(entry)
        if not m:
            continue
        
        date_str, time_str, name, message = m.groups()
        poop_count = entry.count("💩")

        if poop_count == 0:
            continue
        dt = pd.to_datetime(
                f"{date_str} {time_str}",
                format = "%m/%d/%y %H:%M"
        )
        for _ in range(poop_count):
            rows.append({
                "datetime": dt,
                "name": params.NAME_LUT[name]
            })
    df = pd.DataFrame(rows)
    return df

def get_monthly_score(data: pd.DataFrame, month: int): 
    this_month = data[data["datetime"].dt.month == month]
    score_df = (
        this_month.groupby("name")
        .size()
        .reset_index(name="poop_count")
        .sort_values("poop_count", ascending=False)
    )
    score_df["rank"] = score_df["poop_count"].rank(ascending=False, method="dense").astype(int)
    return score_df

def get_yearly_score(data: pd.DataFrame, year: int): 
    this_month = data[data["datetime"].dt.year == year]
    score_df = (
        this_month.groupby("name")
        .size()
        .reset_index(name="poop_count")
        .sort_values("poop_count", ascending=False)
    )
    score_df["rank"] = score_df["poop_count"].rank(ascending=False, method="dense").astype(int)
    return score_df

def build_table(df):
    df = df.reset_index(drop=True)
    df["rank"] = df.index + 1

    return "\n".join(
        f"| {r.rank} | {r.name} | {r.poop_count} |"
        for r in df.itertuples()
    )

def fill_md(data: pd.DataFrame):
    with open("cagadas_report_template.md", "r") as f:
        template = f.read()
    monthly = get_monthly_score(data, 6)
    yearly = get_yearly_score(data, 2026)

    monthly_table = build_table(monthly)
    yearly_table = build_table(yearly)

    # replace placeholders
    final_md = template
    final_md = final_md.replace("{{MONTH}}", "2026-06")
    final_md = final_md.replace("{{YEAR}}", "2026")
    final_md = final_md.replace("{{MONTHLY_TABLE}}", monthly_table)
    final_md = final_md.replace("{{YEARLY_TABLE}}", yearly_table)

    return final_md

def save_report(data: str, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)

def main():
    filename = "cagadas.txt"
    data = parse_file(filename)
    final_md = fill_md(data)
    save_report(final_md, "cagadas_report.md")


if __name__=='__main__':
    main()
