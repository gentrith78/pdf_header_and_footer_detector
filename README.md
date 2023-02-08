# Pdf Header and Dooter Detector
This python script uses a python library for PDF parsing.
With the data extracted from raw PDF, this script will use some advanced algorithms to detect the headers and footers.
# How does the algorithm works:
- It takes each line of text and its coordinates that PdfMiner outputs
- Through coordinates it looks for empty lines on upper paragraphs
- If it finds empty lines in middle of upper or buttom paragraphs it will split the paragraphs based on that space.
- Then it will use difflib sequencematcher and look for similarities beetwen those upper and bottom lines.
- This number of matched paragraphs should be equal to number_of_pages - 2

