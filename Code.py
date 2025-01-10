import csv

def read_and_convert(dat_file, csv_file, delimiter='¸'):
    with open(dat_file, 'r', encoding='utf-8') as infile, open(csv_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        
        current_record = []  # To store fields of the current record

        for line in infile:
            # Strip leading/trailing whitespace, including newlines
            stripped_line = line.strip()
            
            # Skip empty lines
            if not stripped_line:
                continue
            
            # If the line does not end with the delimiter, it's a continuation of the current record
            if not stripped_line.endswith(delimiter):
                # Add the line to the current record, replacing newlines with spaces if needed
                current_record.append(stripped_line)
                # Write the complete record to the CSV
                writer.writerow(current_record)
                current_record = []  # Reset for the next record
            else:
                # Line ends with a delimiter, so it's part of the same record
                current_record.append(stripped_line[:-1])  # Remove the trailing delimiter

        # Write the last record if it exists
        if current_record:
            writer.writerow(current_record)

    print(f"Converted {dat_file} to {csv_file} successfully!")

# Example usage
dat_file = 'input.dat'
csv_file = 'output.csv'
read_and_convert(dat_file, csv_file)
