import pandas as pd
import csv
from utils import check_fldr_read_sampleid

sample_id = check_fldr_read_sampleid()

volcano_data_csv = "input_files/" + sample_id + "_volcano.csv"
part1_xls_loc = "output_files/" + sample_id + "_p1.xlsx"
part1_csv_loc = "output_files/" + sample_id + "-transposed_p1.csv"
part2_csv_loc = "output_files/" + sample_id + "_p2.csv"


# load part 1 xls metadata associated with each compound
xls = pd.ExcelFile(part1_xls_loc)
page_of_interest = pd.read_excel(xls, "Compounds")
desired_columns = ["Formula", "Annot. DeltaMass [ppm]", \
											"Calc. MW", "m/z", "RT [min]", "Area (Max.)", \
											"MS2"]

annotation_data = {}
for index, row in page_of_interest.iterrows():
	# skip over rows with nothing in the Name column
	name = row["Name"]
	if str(name) == "nan":
		continue

	if name not in annotation_data:
		annotation_data[name] = []
	for key in desired_columns:
		value = row[key]
		annotation_data[name].append(value)

# Load lookup of each name to bio group
name_signal_lookup, ordered_groups = {}, []
with open(part1_csv_loc, "r") as f:
	reader = csv.reader(f)

	counter = 0
	for row in reader:
		counter += 1

		if counter == 1:
			# header
			names = row[1:]
			for n in names:
				name_signal_lookup[n] = []
		else:
			# data rows
			group = row[0]
			ordered_groups.append(group)

			signal_array = row[1:]
			for i in range(len(names)):
				n = names[i]
				s = signal_array[i]

				name_signal_lookup[n].append(s)
f.close()

name_volcano_array = {}
names_in_volc = []
with open(volcano_data_csv, "r") as f:
	reader = csv.reader(f)
	next(reader, None)

	for row in reader:
		name, fc, log2_fc, raw_pvalue, neg_log10_pvalue = row
		name_volcano_array[name] = [fc, log2_fc, raw_pvalue, neg_log10_pvalue]

		if name in names:
			names_in_volc.append(name)
f.close()

with open(part2_csv_loc, "w") as f:
	out = csv.writer(f)

	header_row = ["Sample Name"]
	header_row = header_row + names_in_volc
	out.writerow(header_row)

	volcano_index_labels = [
		[0, "FC"], \
		[2, "Raw PValue"], \
	]

	# write out the volcano plot data
	for volc_index, volc_label in volcano_index_labels:
		volc_data_row = [volc_label]
		for n in names_in_volc:
			volc_data = name_volcano_array[n]
			volc_data_row.append(volc_data[volc_index])

		out.writerow(volc_data_row)

	# write out metadata
	for i in range(len(desired_columns)):
		key = desired_columns[i]

		metadata_out_row = [key]
		for n in names_in_volc:
			metadata = annotation_data[n]
			metadata_value = metadata[i]
			metadata_out_row.append(metadata_value)
		out.writerow(metadata_out_row)

	# write out name-group signal data
	for i in range(len(ordered_groups)):
		group = ordered_groups[i]
		ng_signal_data = [group]

		for n in names_in_volc:
			n_group_signal = name_signal_lookup[n][i]
			ng_signal_data.append(n_group_signal)

		out.writerow(ng_signal_data)
f.close()
