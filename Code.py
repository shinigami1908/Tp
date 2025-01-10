import csv

def read_and_convert(dat_file, csv_file, delimiter='¸'):
    with open(dat_file, 'r', encoding='utf-8') as infile, open(csv_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        
        current_record = []  # Holds the current record being processed
        num_columns = None   # Number of columns to expect (inferred from the first complete record)

        for line in infile:
            # Strip newline characters and leading/trailing spaces
            stripped_line = line.strip()
            
            # Skip empty lines
            if not stripped_line:
                continue

            # Split the line into fields based on the delimiter
            fields = stripped_line.split(delimiter)

            # Initialize number of columns based on the first record
            if num_columns is None:
                num_columns = len(fields)

            # If the current record is incomplete, append this line's fields
            if len(current_record) + len(fields) <= num_columns:
                current_record.extend(fields)
            else:
                # Write the completed record to the CSV
                writer.writerow(current_record)
                current_record = fields  # Start a new record

        # Write the last record if it exists
        if current_record:
            writer.writerow(current_record)

    print(f"Converted {dat_file} to {csv_file} successfully!")

# Example usage
dat_file = 'input.dat'
csv_file = 'output.csv'
read_and_convert(dat_file, csv_file)
