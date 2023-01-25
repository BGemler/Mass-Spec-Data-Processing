# Mass-Spec-Data-Processing
This pipeline processes mass spec data for Metaboanalyst 5.0 analysis. Further compound specific reports can also be generated using Metaboanalyst's volcano data.

# Operating Procedure
+ Update SAMPLE_ID.txt with the root sample ID (e.g., "example" is the root sample ID in "example.xlsx")
+ Place the abundance XLS data file in the "input_files" folder
+ Run "python3 part1_annotation_transform.py" from your terminal in the location of this code pipeline
+ Use the file named "{root sample ID} + -transposed_p1.csv" the "output_files" folder for Metaboanalyst 5.0 analysis, looking over results first for gut-check and add sample group IDs
+ Place the resulting volcano plot data in a CSV file in the "input_files" folder, titled "{root sample ID} + _ volcano.csv"
+ Run "python3 part2_compound_trackback.py"
+ The resulting output file, "{root sample ID} + _ p2.csv", located in the "output_files" folder, is the end result of the pipeline for analysis

# Part 1 - Raw Data Handling and Data Transform for Metaboanalyst 5.0 Analysis
# Part 2 - Combine Metaboanalyst 5.0 Volcano Data with Signals for End User Interpretation
