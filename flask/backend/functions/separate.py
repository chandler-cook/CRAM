import re

# Define the pattern to match a description followed by "Score: <number>"
pattern = re.compile(r"(.*?)(Score: \d+)(?=\s|$)")

# Open the file, read its content, and find all matches
with open("vault.txt", "r") as infile:
    content = infile.read()

# Find all matches for the entire content
matches = pattern.findall(content)

# Prepare the formatted entries
formatted_entries = []
for match in matches:
    description = match[0].strip()  # Remove leading/trailing whitespace from description
    score = match[1].strip()  # Remove leading/trailing whitespace from score
    formatted_entries.append(f"{description}\n{score}\n")

# Write the formatted entries to the output file
with open("formatted_vault.txt", "w") as outfile:
    outfile.write("\n".join(formatted_entries))

print("File formatted and saved as 'formatted_vault.txt'")
