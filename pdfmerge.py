#! python3
# Merge all .pdf files in the current directory

import os
import sys
import webbrowser
import requests
from PyPDF2 import PdfReader, PdfMerger
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

def paperless(tag_to_query):
    # PAPERLESS CONSTANTS
    API_URL = "https://paperless.brichet.be/api/documents/"
    AUTH_TOKEN = "08d29963baa1a3ed9a8a0a0f59103b86b0079a3a"  

    # Set up the headers with the authentication token
    headers = {
        'Authorization': f'Token {AUTH_TOKEN}',
    }

    # Make a GET request to the API to retrieve documents with the specific tag
    response = requests.get(API_URL, params={'tags__name__iexact': tag_to_query}, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        documents = response.json()

        # Iterate through the documents and download them
        for document in documents['results']:
            # Download the document
            document_id = document['id']
            document_filename = document['archived_file_name']
            document_url = API_URL+str(document_id)+"/download/"
            document_file = requests.get(document_url, headers=headers)
            
            if document_file.status_code == 200:
                open(document_filename, 'wb').write(document_file.content)
                print(f"Downloaded: {document_filename}")
            else:
                print(f"Failed to download: {document_filename}")
    else:
        print(f"Failed to retrieve documents. Status code: {response.status_code}")


# Get output filename from arguments
if len(sys.argv) <= 1:
    print('Missing Argument : pdfmerge.py "OutputFile.pdf" ["Paperless Tag Between Quotes"]')
    sys.exit(1)
if sys.argv[1][-4:] != '.pdf':
    print('Output file extension must be .pdf')
    sys.exit(1)
if len(sys.argv) == 3:
    paperless(sys.argv[2])
    

OutputFile = sys.argv[1]

# Remove Merged file if exists
if os.path.exists(OutputFile):
    os.remove(OutputFile)

# Get all the .pdf files in current directory
pdfFiles = []
for filename in os.listdir('.'):
    if filename.endswith('.pdf'):
        pdfFiles.append(filename)
pdfFiles.sort(key = str.casefold)
pdfMerger = PdfMerger()

# Loop through all the pdf files
for filename in pdfFiles:
    pdfMerger.append(filename, import_outline=False,outline_item=str(filename))

pdfMerger.write(OutputFile)

# Read newly created PDF to extract bookmarks
pdffile = PdfReader(OutputFile)
outline = pdffile.outline

# # Create Text File for fun
# f = open('bookmarks.txt',"w+")
# for x in outline:
#     f.write('{:.<60} {:d}'.format(x.get("/Title"),x.get("/Page")+2)+'\n')
# f.close()

# Create PDF File
style = ParagraphStyle(
        name='Normal',
        fontName='Courier',
        fontSize=10,
        )
story = []

pdf_name = 'bookmarks.pdf'
doc = SimpleDocTemplate(
    pdf_name,
    pagesize=letter,
    bottomMargin=.4 * inch,
    topMargin=.6 * inch,
    rightMargin=.8 * inch,
    leftMargin=.8 * inch
    )

text_content = ""

for x in outline:
    text_content += '{:.<70} {:d}'.format(x.get("/Title"),x.get("/Page")+2)
    text_content += '<br/>'
                    

P = Paragraph(text_content, style)
story.append(P)

doc.build(
    story,
)

# Merge TOC and Merged PDF
pdfMerger = PdfMerger()
pdfMerger.merge(0,'bookmarks.pdf',import_outline=False)
pdfMerger.append(PdfReader(OutputFile))
pdfMerger.write(OutputFile)
pdfMerger.close()

# Remove bookmarks.pdf file if exists
if os.path.exists('bookmarks.pdf'):
    os.remove('bookmarks.pdf')

# Open PDF file (change to webbrowser to have linux compatibility)
webbrowser.open_new(OutputFile)
