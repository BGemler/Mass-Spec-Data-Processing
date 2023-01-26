import os
import subprocess


def check_fldr_read_sampleid():
	"""
	"""
	with open("SAMPLE_ID.txt", "r") as f:
		for row in f:
			sample_id = row.replace("\n","")
			break
	f.close()

	fldrs_to_check = ["input_files/", "output_files/"]
	for fldr in fldrs_to_check:
		if os.path.isdir(fldr) == False:
			os.makedirs(fldr)

	return sample_id
