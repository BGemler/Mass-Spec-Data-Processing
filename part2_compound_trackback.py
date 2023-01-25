import pandas as pd
import csv
from utils import check_fldr_read_sampleid

sample_id = check_fldr_read_sampleid()

volcano_data_csv = "input_files/" + sample_id + "_volcano.csv"
part1_csv_loc = "output_files/" + sample_id + "-transposed_p1.csv"
part2_csv_loc = "output_files/" + sample_id + "_p2.csv"

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
		[1, "Log 2 FC"], \
		[2, "Raw PValue"], \
		[3, "Negative Log10 PValue"]
	]

	# write out the volcano plot data
	for volc_index, volc_label in volcano_index_labels:
		volc_data_row = [volc_label]
		for n in names_in_volc:
			volc_data = name_volcano_array[n]
			volc_data_row.append(volc_data[volc_index])

		out.writerow(volc_data_row)

	# write out name-group signal data
	for i in range(len(ordered_groups)):
		group = ordered_groups[i]
		ng_signal_data = [group]

		for n in names_in_volc:
			n_group_signal = name_signal_lookup[n][i]
			ng_signal_data.append(n_group_signal)

		out.writerow(ng_signal_data)
f.close()
