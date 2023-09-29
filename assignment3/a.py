import re

def extract_data(input_text):
    parts = input_text.split("\n\n", 1)
    return parts[1]
# Sample input text
input_text = """
Some text before
Offset: 1400
NumBytes: 1400

This is the content you want to extract.
There could be more text here.


This is another section.
More text after
"""

# Call the function with the sample input
result = extract_data(input_text)
print(result)
