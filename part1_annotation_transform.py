import pandas as pd
import numpy as np
import statistics
from utils import check_fldr_read_sampleid

sample_id = check_fldr_read_sampleid()

og_compound_loc = "input_files/" + sample_id + ".xlsx"
part1_xls_loc = "output_files/" + sample_id + "_p1.xlsx"
part1_csv_loc = "output_files/" + sample_id + "-transposed_p1.csv"

# Part 1 step 1 - remove unwanted column headers
# Remove rows w/out Name 
# Highlight cells with "full match" under mzCloud Search, mzVault Search, OR MassList Search
xls_writer = pd.ExcelWriter(part1_xls_loc, engine='xlsxwriter', \
														engine_kwargs={'options': {'strings_to_numbers': True}})

xls = pd.ExcelFile(og_compound_loc)
page_of_interest = pd.read_excel(xls, "Compounds")

unneeded_columns = ["Tags", "Checked", "Annot. Source: Predicted Compositions", \
											"Annot. Source: Metabolika Search", "Annot. Source: ChemSpider Search"]
desired_columns = []
annotation_data = {}

for key in page_of_interest.keys():
	if key not in unneeded_columns:
		desired_columns.append(key)
		annotation_data[key] = []	

for index, row in page_of_interest.iterrows():
	# skip over rows with nothing in the Name column
	name = row["Name"]
	if str(name) == "nan":
		continue

	for key in desired_columns:
		value = row[key]
		annotation_data[key].append(value)

# Create post-Part 1 Step 1 Excel file
page_of_interest.to_excel(xls_writer, sheet_name="Compounds", index = False)

Annotation_df = pd.DataFrame(data = annotation_data)
Annotation_df.to_excel(xls_writer, sheet_name="Annotation", index = False)

# add conditional formatting to highlight full match cells
workbook = xls_writer.book
format1 = workbook.add_format({'bg_color': '#ADD8E6', 
																'font_color': '#00008B'})

worksheet = xls_writer.sheets['Annotation']
worksheet.conditional_format('C1:E' + str(len(Annotation_df)),
															{'type': 'text', 
																'criteria': 'containing', 
																'value': 'Full match',
																'format': format1})

# Part 1 step 2 - QC CV
# Need to add 4 columns - Bio averages, QC averages, QC StDev, QC CV
step2_desired_columns = [desired_columns[0]] + \
														["Biological Averages", "QC Averages", "QC StDev", "QC CV"] + \
														desired_columns[1:]
# find bio columns, QC columns
bio_cols, qc_cols = [], []
for col in desired_columns:
	if "Group Area" in col and "Pos-QC" in col:
		qc_cols.append(col)
	if "Group Area" in col and "Pos-" in col and "QC" not in col:
		bio_cols.append(col)

# init QC dataframe
qc_data = {}
for key in step2_desired_columns:
	qc_data[key] = []

# parse thru rows, make calculations
for index, row in Annotation_df.iterrows():
	bio_values, qc_values = [], []
	for key in bio_cols:
		bio_values.append(row[key])
	for key in qc_cols:
		qc_values.append(row[key])

	# calculations
	bio_average = np.average(bio_values)
	qc_average = np.average(qc_values)
	qc_stdev = statistics.stdev(qc_values)
	qc_cv = qc_stdev / qc_average

	# add to dict
	for key in step2_desired_columns:
		if key in row:
			qc_data[key].append(row[key])
		elif key == "Biological Averages":
			qc_data[key].append(bio_average)
		elif key == "QC Averages":
			qc_data[key].append(qc_average)
		elif key == "QC StDev":
			qc_data[key].append(qc_stdev)
		elif key == "QC CV":
			qc_data[key].append(qc_cv)

QC_CV_df = pd.DataFrame(data = qc_data)
QC_CV_df.to_excel(xls_writer, sheet_name="QC CV", index = False)

# add conditional formatting to QC CV sheet
worksheet = xls_writer.sheets['QC CV']
worksheet.conditional_format('G1:I' + str(len(QC_CV_df)),
															{'type': 'text', 
																'criteria': 'containing', 
																'value': 'Full match',
																'format': format1})

# Part 1 step 3 - Compound assignment
# parse thru rows, delete low CV and collect duplicates
signal_array = {}
for index, row in QC_CV_df.iterrows():
	qc_cv = row["QC CV"]

	if qc_cv > 0.25:
		continue

	name = row["Name"]
	bio_avg = row["Biological Averages"]

	if name not in signal_array:
		signal_array[name] = []
	signal_array[name].append([index, bio_avg])

# parse thru signals, identify duplicates, and if there are any only keep top bio average
indexes_to_keep = []
for name in signal_array:
	data_rows = signal_array[name]

	max_bio_avg = 0.0
	for index, bio_avg in data_rows:
		if bio_avg > max_bio_avg:
			max_bio_avg = bio_avg

	for index, bio_avg in data_rows:
		if bio_avg == max_bio_avg:
			indexes_to_keep.append(index)
			break

# init compound assignment dataframe
compound_assignment = {}
for key in step2_desired_columns:
	compound_assignment[key] = []

# Collect and write out compound assignmnet data passing restrictions
for index, row in QC_CV_df.iterrows():
	if index not in indexes_to_keep:
		continue

	for key in step2_desired_columns:
		compound_assignment[key].append(row[key])

compound_assign_df = pd.DataFrame(data = compound_assignment)
compound_assign_df.to_excel(xls_writer, sheet_name="Compound Assignment", index = False)

# add conditional formatting to QC CV sheet
worksheet = xls_writer.sheets['Compound Assignment']
worksheet.conditional_format('G1:I' + str(len(compound_assign_df)),
															{'type': 'text', 
																'criteria': 'containing', 
																'value': 'Full match',
																'format': format1})

xls_writer.save()

# make a DF to cut down to desired columns
csv_desired_cols = [step2_desired_columns[0]] + bio_cols + qc_cols
transpose_assignment = {}
for key in csv_desired_cols:
	transpose_assignment[key] = []

for index, row in compound_assign_df.iterrows():
	for key in csv_desired_cols:
		transpose_assignment[key].append(row[key])

# get transform for entry to Metaboanalyst 5.0
final_data = pd.DataFrame(data = transpose_assignment)
final_data_transpose = final_data.transpose()
final_data_transpose.to_csv(part1_csv_loc, header = False)

