#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json

from io import StringIO
from urllib import request

from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams


def get_pdf_info(url):
    password = ''  # If any password set for pdf opening
    page_no = set()
    max_pages = 10  # Set the maximum pages to be extracted
    caching = True
    la_params = LAParams()  # Performing Layout Analysis
    output_fp1 = StringIO()
    resource_object = PDFResourceManager(caching=caching)  # Used to store shared resources such as fonts or images in pdf.
    opener = request.FancyURLopener({})

    # Adding headers for opening pdf online if needed

    opener.addheaders = [('User-agent',
                         'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0'
                         ), ('Connection', 'keep-alive')]
    fp = opener.open(url)
    device = TextConverter(resource_object, output_fp1,
                           laparams=la_params)

    f = process_pdf(
        resource_object,
        device,
        fp,
        page_no,
        maxpages=max_pages,
        password=password,
        caching=caching,
        check_extractable=True,
        )

    # Task done by process_pdf
    # 1.Process pdf - first create a parse object for the corresponding pdf
    # 2.Bypassing the password protected document
    # 3.Checking if the given pdf is extractable or not
    # 4.If extractable parse the pages till max_pages limit given

    fp.close()
    device.close()
    ctx = get_paragraphs(output_fp1.getvalue().strip())
    return ctx


def get_paragraphs(text):
    """
    Manipulating the extracted raw data of process_pdf as title and only description.
    Getting paragraphs and title if present.
    :param text: string
    :return title , description: json
    """

    return_title = ''
    return_val = ''
    buffer = ''
    para_count = 0
    for line in text.splitlines():

        # Remove the final '-'
        # print (line)
        # TODO: Fix this

        if line.endswith('-'):
            line = line[:-1]

        # If line is empty (\n only) then we probably ended
        # a paragraph, so add buffer to return_val

        if line == '':

            # Some paragraphs should be skipped

            accept_para = True

            # Criterion 1: Number of words in paragraph to be
            #              greater than 10
            # Criterion 2: If return_title is null, then the first line that doesn't have anything stupid may be
            #              the title. Also should have more than 3 words

            if return_title == '':
                if len(buffer.split()) > 3:
                    if any(c.isalpha() for c in buffer):
                        return_title = buffer

                    # Set flag for title so that it is not included in description

                    accept_para = False

            if len(buffer.split()) < 10:
                accept_para = False
            if accept_para:
                return_val += buffer

                para_count += 1
            buffer = ''
        else:

            # Some lines should be skipped.

            accept_line = True

            # Criterion 1: Line should not contain more than 4 consecutive special characters (.,#,/,\)

            if re.search('\.\.\.\.', line) or re.search('\#\#\#\#',
                    line) or re.search('\\\\\\\\', line) \
                or re.search('\/\/\/\/', line):
                accept_line = False
            if accept_line:
                buffer += line
                buffer += ' '

        if para_count == 10:  # only extract till paragraph count is 10
            break
    return json.dumps({'title': return_title,
                      'description': return_val})


# text = get_pdf_info("http://unec.edu.az/application/uploads/2014/12/pdf-sample.pdf") #Sample pdf

text = get_pdf_info('http://www.pdf995.com/samples/pdf.pdf')  # Sample pdf
extracted_data = text
