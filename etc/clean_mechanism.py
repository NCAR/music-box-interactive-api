import json
import sys

# Read the JSON file
# Check if the command-line argument is provided
if len(sys.argv) < 2:
    print("Please provide the path to the JSON file as a command-line argument.")
    print("Example: python clean_mechanism.py path/to/file.json")
    print("NOTE: You will have to remove the quotes from around the Ea values in the JSON file.")
    sys.exit(1)

# Get the path to the JSON file from the command-line argument
json_file_path = sys.argv[1]

# Read the JSON file
with open(json_file_path) as file:
    data = json.load(file)

# Loop through the array of objects
for obj in data["camp-data"][0]["reactions"]:
    # Check if the object has "type" = "ARRHENIUS"
    if obj.get("type") == "ARRHENIUS":
        # Replace the "C" element with "Ea" whose value is the negative of the "C" value
        obj["Ea"] = format(-obj["C"] * 1.380649e-23, ".8e")
        del obj["C"]

# Write the modified data back to the JSON file
with open(json_file_path, "w") as file:
    json.dump(data, file)
