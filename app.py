import tkinter as tk
from tkinter import messagebox, ttk


def calculate_project():
	try:
		head = float(head_entry.get())
		flow = float(flow_entry.get())
		capacity_factor = float(capacity_entry.get()) / 100
		tariff = float(tariff_entry.get())
		cost_per_mw = float(cost_entry.get())
		project_cost = float(cost_total_entry.get())
		annual_opex = float(opex_entry.get())
	except ValueError:
		messagebox.showerror("Check inputs", "Enter numbers in every field.")
		return

	if min(head, flow, capacity_factor, tariff, cost_per_mw, project_cost, annual_opex) < 0:
		messagebox.showerror("Check inputs", "Values cannot be negative.")
		return
	if capacity_factor > 1:
		messagebox.showerror("Check inputs", "Capacity factor must be between 0 and 100%.")
		return

	installed_mw = 9.81 * head * flow * 0.88 / 1000
	annual_energy_gwh = installed_mw * 8760 * capacity_factor / 1000
	annual_revenue = annual_energy_gwh * 1_000_000 * tariff
	annual_profit = annual_revenue - annual_opex * 1_000_000
	payback = project_cost / annual_profit if annual_profit > 0 else None
	estimated_capex = installed_mw * cost_per_mw

	result_values = [
		("Estimated capacity", f"{installed_mw:,.2f} MW"),
		("Annual generation", f"{annual_energy_gwh:,.2f} GWh"),
		("Annual revenue", f"NPR {annual_revenue / 1_000_000:,.2f} million"),
		("Annual operating profit", f"NPR {annual_profit / 1_000_000:,.2f} million"),
		("Simple payback", f"{payback:,.1f} years" if payback else "Not viable"),
		("Indicative construction cost", f"NPR {estimated_capex:,.2f} million"),
	]
	for label, value in result_values:
		result_labels[label].config(text=value)

	if annual_profit > 0 and payback <= 12:
		status_label.config(text="PROMISING", foreground="#176b45")
	elif annual_profit > 0:
		status_label.config(text="NEEDS OPTIMIZATION", foreground="#a15c00")
	else:
		status_label.config(text="NOT VIABLE", foreground="#a13232")


def add_input(parent, row, label, default, unit):
	ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=6)
	entry = ttk.Entry(parent, width=16)
	entry.insert(0, default)
	entry.grid(row=row, column=1, sticky="e", pady=6)
	ttk.Label(parent, text=unit, foreground="#64748b").grid(row=row, column=2, sticky="w", padx=(8, 0))
	return entry


root = tk.Tk()
root.title("Himalayan Flow | Nepal Hydropower Planner")
root.geometry("920x620")
root.minsize(760, 540)
root.configure(bg="#f4f7f6")

style = ttk.Style(root)
style.theme_use("clam")
style.configure("TFrame", background="#f4f7f6")
style.configure("Panel.TFrame", background="#ffffff")
style.configure("TLabel", background="#ffffff", foreground="#173b3f", font=("Segoe UI", 10))
style.configure("Title.TLabel", background="#f4f7f6", foreground="#173b3f", font=("Georgia", 24, "bold"))
style.configure("Subtitle.TLabel", background="#f4f7f6", foreground="#527174", font=("Segoe UI", 10))
style.configure("Section.TLabel", background="#ffffff", foreground="#176b45", font=("Segoe UI", 11, "bold"))
style.configure("Accent.TButton", background="#176b45", foreground="#ffffff", padding=(18, 10), font=("Segoe UI", 10, "bold"))

header = ttk.Frame(root)
header.pack(fill="x", padx=34, pady=(28, 18))
ttk.Label(header, text="Himalayan Flow", style="Title.TLabel").pack(anchor="w")
ttk.Label(header, text="Early-stage hydropower feasibility for Nepal's river corridors", style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))

content = ttk.Frame(root)
content.pack(fill="both", expand=True, padx=34, pady=(0, 28))
content.columnconfigure(0, weight=1)
content.columnconfigure(1, weight=1)
content.rowconfigure(0, weight=1)

inputs = ttk.Frame(content, style="Panel.TFrame", padding=24)
inputs.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
results = ttk.Frame(content, style="Panel.TFrame", padding=24)
results.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

ttk.Label(inputs, text="SITE & FINANCE ASSUMPTIONS", style="Section.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
head_entry = add_input(inputs, 1, "Gross head", "80", "m")
flow_entry = add_input(inputs, 2, "Design flow", "12", "m³/s")
capacity_entry = add_input(inputs, 3, "Capacity factor", "45", "%")
tariff_entry = add_input(inputs, 4, "Electricity tariff", "8.50", "NPR/kWh")
cost_entry = add_input(inputs, 5, "Build cost", "220", "NPR million/MW")
cost_total_entry = add_input(inputs, 6, "Total project cost", "2500", "NPR million")
opex_entry = add_input(inputs, 7, "Annual O&M", "45", "NPR million")

ttk.Button(inputs, text="CALCULATE FEASIBILITY", style="Accent.TButton", command=calculate_project).grid(row=8, column=0, columnspan=3, sticky="ew", pady=(22, 8))
ttk.Label(inputs, text="Screening estimate only. Confirm hydrology, EIA, licensing, grid access, and financing with qualified specialists.", wraplength=330, foreground="#64748b").grid(row=9, column=0, columnspan=3, sticky="w", pady=(10, 0))

ttk.Label(results, text="PROJECT SIGNAL", style="Section.TLabel").grid(row=0, column=0, sticky="w")
status_label = ttk.Label(results, text="READY", font=("Segoe UI", 16, "bold"), foreground="#527174")
status_label.grid(row=1, column=0, sticky="w", pady=(6, 20))
result_labels = {}
for row, (label, initial) in enumerate([
	("Estimated capacity", "—"),
	("Annual generation", "—"),
	("Annual revenue", "—"),
	("Annual operating profit", "—"),
	("Simple payback", "—"),
	("Indicative construction cost", "—"),
], start=2):
	ttk.Label(results, text=label, foreground="#64748b").grid(row=row, column=0, sticky="w", pady=(7, 0))
	value_label = ttk.Label(results, text=initial, font=("Segoe UI", 12, "bold"))
	value_label.grid(row=row + 1, column=0, sticky="w", pady=(0, 7))
	result_labels[label] = value_label

results.columnconfigure(0, weight=1)
calculate_project()
root.mainloop()
