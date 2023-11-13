from fitz import (
    Document, Page, Rect, TEXT_ALIGN_CENTER,
    TEXT_ALIGN_RIGHT, PDF_REDACT_IMAGE_NONE, PDF_ENCRYPT_KEEP
)

from compiloor.constants.utils import (
    PAGE_NUMBER_FONT_SIZE, PAGE_NUMBER_FOR_SECTION_FONT_SIZE, PRIMARY_COLOR_IN_PERCENTAGES
)

# Rewrite this method with more elegant code.    
def create_report_with_page_numbers_and_legend(report_path: str, report_section_headings: list[str]) -> None:
    """
        Creates a new report with page numbers and a legend for the findings.
    """

    new_pdf = Document(report_path) # Using fitz to edit the PDF.
        
    pages_to_delete: list[int] = []
    
    page: Page    
    
    page_to_index: dict[str, int] = {}
    page_to_index_occurences: dict[str, int] = {}
    
    for page in new_pdf.pages():
        if page.get_textpage().extractText() == "": 
            pages_to_delete.append(page.number) 
            continue
        page.clean_contents()
        
    if len(pages_to_delete): new_pdf.delete_pages(pages_to_delete) # Deleting empty pages.

    # Normalizing the page orientations:    
    for page in new_pdf.pages():
        if page.number == 0: continue         
        x1, y1 = page.cropbox.x1, page.cropbox.y1 # Getting the dimensions of the page.

        page.clean_contents()
        
        # Insert page numbers on each page:
        page.insert_textbox(
            # The whole width of the page for the last 25th of the page vertically:
            Rect(0, y1 - y1 / 25, x1, y1),
            str(page.number),
            align = TEXT_ALIGN_CENTER,
            fontsize = PAGE_NUMBER_FONT_SIZE,
            color = PRIMARY_COLOR_IN_PERCENTAGES
        )
                    
        page_text: str = page.get_textpage().extractText().replace("\n", " ").replace("  ", " ")
                                            
        for index in range(len(report_section_headings)):
            heading = report_section_headings[index]

            # Chopping the heading if it's too long so that we can find a complete fragment in the page:
            if len(heading) > 38:
                heading = heading[:38]
                report_section_headings[index] = heading

            if "`" in heading: 
                heading = heading.split("`")[0]
                report_section_headings[index] = heading

            if not heading in page_text:
                continue
                                    
            if heading in page_to_index: continue
            
            if not heading in page_to_index_occurences: 
                page_to_index_occurences[heading] = 0

            page_to_index_occurences[heading] += 1

            # Different if statements to avoid long lines of logic:
            if page_to_index_occurences[heading] < 2: continue

            if page_to_index_occurences[heading] < 3 and heading.startswith("["): continue

            # Setting the page number for the section:
            page_to_index[heading] = page.number

    for section in page_to_index.keys():
        for page in new_pdf.pages():
            index = section.split(" ")[0]

            index = index if not "." in index else index[:-1]
            
            search_fragment: str = '{{[' + index + ']_page}}' if not '[' in index and not ']' in index else '{{' + index + '_page}}'

            # Trying to find the fragment's coordiantes on the page:
            fragment = page.search_for(search_fragment)
                
            if not fragment: continue

            page.add_redact_annot(
                fragment[0],
                str(page_to_index[section]),
                cross_out=False,
                align=TEXT_ALIGN_RIGHT,
                fontsize = PAGE_NUMBER_FOR_SECTION_FONT_SIZE,
                text_color = PRIMARY_COLOR_IN_PERCENTAGES
            )
            page.apply_redactions(images=PDF_REDACT_IMAGE_NONE)
            break
        
    new_pdf.save(report_path, incremental=True, encryption=PDF_ENCRYPT_KEEP)