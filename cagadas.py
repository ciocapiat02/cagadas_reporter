import re
from matplotlib.ticker import MaxNLocator
import pandas as pd
import matplotlib.pyplot as plt
import params
import os

def check_output_dir(dirname: str):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

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

def plot_month_for_name(data: pd.DataFrame, name: str):
    named = data[data["name"] == name].copy()

    # ensure datetime
    named["datetime"] = pd.to_datetime(named["datetime"])

    # infer month range from data
    start = named["datetime"].dt.to_period("M").dt.start_time.iloc[0]
    end = named["datetime"].dt.to_period("M").dt.end_time.iloc[0]

    # full daily range for that month
    full_range = pd.date_range(start=start, end=end, freq="D")

    # count per day
    daily_counts = (
        named.set_index("datetime")
             .resample("D")
             .size()
             .reindex(full_range, fill_value=0)
    )

    plt.figure(figsize=(10, 4), facecolor=params.PLOT_COLORS["background"])
    plt.plot(
        daily_counts.index.astype(str),
        daily_counts.values,
        linewidth=2,
        marker="o",
        markerfacecolor=params.PLOT_COLORS["marker"],
        markeredgecolor=params.PLOT_COLORS["marker"],
        color=params.PLOT_COLORS["marker"],
    )

    ax = plt.gca()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.label.set_color(params.PLOT_COLORS["foreground"])
    ax.yaxis.label.set_color(params.PLOT_COLORS["foreground"])
    ax.set_facecolor(params.PLOT_COLORS["background"])
    ax.spines['bottom'].set_color(params.PLOT_COLORS["foreground"])
    ax.spines['top'].set_color(params.PLOT_COLORS["foreground"])
    ax.spines['left'].set_color(params.PLOT_COLORS["foreground"])
    ax.spines['right'].set_color(params.PLOT_COLORS["foreground"])
    ax.title.set_color(params.PLOT_COLORS["foreground"])
    ax.tick_params(axis='x', colors=params.PLOT_COLORS["foreground"])
    ax.tick_params(axis='y', colors=params.PLOT_COLORS["foreground"])

    plt.title(f"{name}'s cagadas")
    plt.xlabel("date")
    
    plt.ylabel("cagadas")

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(f"{params.OUTPUT_DIR}/{name}s_cagadas.png")
    plt.close()

    return f"{params.OUTPUT_DIR}/{name}s_cagadas.png"

def build_table(df):
    df = df.reset_index(drop=True)
    df["rank"] = df.index + 1

    return "\n".join(
        f"| {r.rank} | {r.name} | {r.poop_count} |"
        for r in df.itertuples()
    )

def fill_personal_statistics(images):
    final = ""
    for name in images:
        image = images[name]
        final += f"## {name}\n"
        final += f"<img src={image} />\n"
        final += "\n"
    return final



def fill_md(data: pd.DataFrame, images: dict):
    with open(params.REPORT_TEMPLATE, "r") as f:
        template = f.read()
    monthly = get_monthly_score(data, 6)
    yearly = get_yearly_score(data, 2026)

    monthly_table = build_table(monthly)
    yearly_table = build_table(yearly)

    personal_statistics = fill_personal_statistics(images)

    # replace placeholders
    final_md = template
    final_md = final_md.replace("{{MONTH}}", "2026-06")
    final_md = final_md.replace("{{YEAR}}", "2026")
    final_md = final_md.replace("{{MONTHLY_TABLE}}", monthly_table)
    final_md = final_md.replace("{{YEARLY_TABLE}}", yearly_table)
    final_md = final_md.replace("{{PERSONAL_STATISTICS}}", personal_statistics)

    return final_md

def save_report(data: str, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)

def main():
    check_output_dir(params.OUTPUT_DIR)
    data = parse_file(params.DATA_FILENAME)
    image_files = {}
    for i in params.NAME_LUT:
        name = params.NAME_LUT[i]
        image = plot_month_for_name(data, name)
        image_files[name] = image
    final_md = fill_md(data, image_files)
    save_report(final_md, params.REPORT_FILENAME)


if __name__=='__main__':
    main()
