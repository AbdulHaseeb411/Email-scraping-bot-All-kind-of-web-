import pandas as pd

# Function to extract the 'Status' column and save it to a new file
def extract_status_column(input_file, output_file):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Ensure the 'Status' column exists
    if 'Status' in df.columns:
        # Extract the 'Status' column
        status_column = df[['Status']]

        # Save the extracted 'Status' column to a new CSV file
        status_column.to_csv(output_file, index=False)
        print(f"Status column extracted and saved to '{output_file}'")
    else:
        print("Error: 'Status' column not found.")

# Define input and output file paths
input_path = 'Clean-Email0.csv'  # Replace with the path to your input file
output_path = 'Email-Only.csv'  # Replace with the path to your output file

# Call the function to extract the 'Status' column
extract_status_column(input_path, output_path)