import csv

def convert_dat_to_csv(dat_file, csv_file, expected_columns, delimiter='¸'):
    with open(dat_file, 'r', encoding='utf-8') as infile, open(csv_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        
        current_record = []  # To accumulate parts of a single record

        for line in infile:
            # Clean up leading/trailing spaces (but keep logical newline handling intact)
            stripped_line = line.strip()

            # Skip empty lines
            if not stripped_line:
                continue

            # Count the number of delimiters in the line
            delimiter_count = stripped_line.count(delimiter)

            # Append the current line to the ongoing record
            current_record.append(stripped_line)

            # If the delimiter count matches expected_columns - 1, the record is complete
            if delimiter_count == expected_columns - 1:
                # Combine the accumulated lines into a single record
                full_record = delimiter.join(current_record)
                fields = full_record.split(delimiter)

                # Write the complete record to the CSV file
                writer.writerow(fields)

                # Reset for the next record
                current_record = []

        # Handle any leftover record (in case the file ends with an incomplete newline)
        if current_record:
            full_record = delimiter.join(current_record)
            fields = full_record.split(delimiter)
            writer.writerow(fields)

    print(f"Converted {dat_file} to {csv_file} successfully!")
