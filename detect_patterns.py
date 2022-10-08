from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTText,LTTextLine,LTTextBox,LTTextGroup,LTTextBoxHorizontal,LTRect

from difflib import SequenceMatcher
def similar(table, miner):
    return SequenceMatcher(None, table, miner).ratio()
headers_footers = []
def get_HeadAndFoot_miner(path, writeToexcel=False):
    # Open a PDF file.
    sorted_footer_units = []
    sorted_header_units = []
    headers_footers = []
    fp = open(path, 'rb')
    parser = PDFParser(fp)
    device = PDFPageAggregator(PDFResourceManager(),laparams=LAParams(line_overlap=0.5,line_margin=0.5,char_margin= 0.5,detect_vertical=False))
    interpreter = PDFPageInterpreter(PDFResourceManager(), device)
    page_nr = 0
    for page in PDFPage.create_pages(PDFDocument(parser)):
        page_nr+=1
        p_height = page.mediabox[3]
        interpreter.process_page(page)
        layout = device.get_result()
        units = []
        for element in layout:
            if isinstance(element, LTTextBoxHorizontal):
                paragraph = element.get_text()
                if not paragraph.isspace():
                    units.append({'page':page_nr,'para':paragraph,'x0':element.bbox[0],'y0':element.bbox[1]})
            else:
                pass
        if not units:
            continue
        most_bottom_unit = sorted(units, key=lambda d: d['y0'], reverse=False)
        footer_area_units = []
        header_area_units = []
        #there is the unit that has the largest y0 so it is at the tom, and i want to get [-1] since this list is sorted by the smallest y0 so smallest y0 is the first index and largest is the last index marked with [-1]
        headers = [most_bottom_unit[-1]]
        #theopposite of headers
        footers = [most_bottom_unit[0]]
        #check if there is any other unit close enough to be consider as the same line and if yes add it to its corresponding list (header,footer)
        for el in most_bottom_unit:
            smallest = most_bottom_unit[0]['y0']
            largest = most_bottom_unit[-1]['y0']
            if (el['y0']-smallest) >= 0 and (int(el['y0'])-int(smallest)) < 3:
                if el['para'] != most_bottom_unit[0]['para']:
                    footers.append(el)
                    continue
                else:
                    continue
            if (largest - float(el['y0'])) >= 0 and (largest - float(el['y0'])) < 3:
                if el['para'] != most_bottom_unit[-1]['para']:
                    headers.append(el)
                    continue
                else:
                    continue
            if int(el['y0']) - p_height/2 >= 0:
                header_area_units.append(el)
            if int(el['y0']) - p_height/2 < 0:
                footer_area_units.append(el)
        header_area_units = sorted(header_area_units, key=lambda d: d['y0'], reverse=True)
        sorted_footer_units.append(footer_area_units)
        sorted_header_units.append(header_area_units)
        headers = sorted(headers, key=lambda d: d['x0'], reverse=False)
        headers = (el['para'] for el in headers)
        footers = sorted(footers, key=lambda d: d['x0'], reverse=False)
        footers = (el['para'] for el in footers)
        header = '!!??!!'.join(headers)
        footer = '!!??!!'.join(footers)
        headers_footers.append({'page':page_nr,'header':" ".join(header.split()),'footer':" ".join(footer.split())})
    footers = []
    headers = []

    #------------------------------------------------------
    counter_in_loop_hf = 0
    while True:
        units_with_same_index = []
        i_break = False
        for el in sorted_footer_units:
            try:
                units_with_same_index.append(el[counter_in_loop_hf])
            except Exception as e:
                pass
        for unitt in units_with_same_index:
            similar_counter = 0
            for rest in units_with_same_index:

                if similar(unitt['para'],rest['para']) > 0.8:
                    similar_counter += 1
            if similar_counter > (page_nr-5):
                a = " ".join(unitt['para'].split())
                for el in headers_footers:
                    if el['page'] == unitt['page']:
                        el['footer'] = str(el['footer']+'!!??!!'+a)
            else:
                i_break = True
        if i_break:
            break
        counter_in_loop_hf +=1
    #_____________
    counter_in_loop_hf = 0
    while True:
        units_with_same_index = []
        i_break = False
        for el in sorted_header_units:
            try:
                units_with_same_index.append(el[counter_in_loop_hf])
            except Exception as e:
                pass
        for unitt in units_with_same_index:
            similar_counter = 0
            for rest in units_with_same_index:
                if similar(unitt['para'],rest['para']) > 0.8:
                    similar_counter += 1
            if similar_counter > (page_nr-5):
                a = " ".join(unitt['para'].split())
                for el in headers_footers:
                    if el['page'] == unitt['page']:
                        el['header'] = str(el['header']+'!!??!!'+a)
            else:
                i_break = True
        if i_break:
            break
        counter_in_loop_hf +=1
    #------------------------------------------------------
    for el in headers_footers:
        counter_f = 0
        counter_h = 0
        for rest in headers_footers:
            if similar(el['footer'],rest['footer']) > 0.7:
                counter_f +=1
        for rest in headers_footers:
            if similar(el['header'],rest['header']) > 0.7:
                counter_h +=1
        if counter_f >= len(headers_footers) -3:
            footers.append({'page':el['page'],'footers':el['footer'].split(sep='!!??!!')})
        if counter_h >= len(headers_footers) -3:
            headers.append({'page':el['page'],'headers':el['header'].split(sep='!!??!!')})
    return {'headers':headers,'footers':footers}



