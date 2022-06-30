import re
from typing import List, Tuple

import PyPDF2

LEN_HEADER_ROW = 38
LEN_OLD_HEADER_ROW = 37
LEN_SECTION_ROW = 20
LEN_COURSE_TOTAL_ROW = LEN_COLLEGE_TOTAL_ROW = LEN_DEPT_TOTAL_ROW = 19

LETTERS = ["A", "B", "C", "D", "F", "I", "S", "U", "Q", "X"]


def is_header_row(string: str) -> bool:
    """Used to identify whether a row is a header row or not in PDFs
    from or after 2017.

    Args:
        string: The first element in the row
    Returns:
        Whether the row is a header row or not.
    """
    return string == "SECTION"


def is_old_header_row(string: str) -> bool:
    """Used to identify whether a row is a header row or not in PDFs
    before 2017.

    Args:
        string: The first element in the row
    Returns:
        Whether the row is a header row or not.
    """
    return string == "COLLEGE:"


def is_course_total_row(string: str) -> bool:
    """Used to identify whether a row is a course total row or not.

    Args:
        string: The first element in the row
    Returns:
        Whether the row is a course total row or not.
    """
    return string == "COURSE TOTAL:"


def is_dept_total_row(string: str) -> bool:
    """Used to identify whether a row is a department total row or not.

    Args:
        string: The first element in the row
    Returns:
        Whether the row is a department total row or not.
    """
    return string == "DEPARTMENT TOTAL:"


def is_college_total_row(string: str) -> bool:
    """Used to identify whether a row is a college total row or not.

    Args:
        string: The first element in the row
    Returns:
        Whether the row is a department total row or not.
    """
    return string == "COLLEGE TOTAL:"


def sanitize_page(page_obj: PyPDF2.PageObject) -> List[str]:
    """Splits a PageObject's content on any number of newlines, and returns
    the content as a list of strings.

    Args:
        page_obj: The content of a PDF page
    Returns:
        A list of strings representing the content on the page.
    """
    text = page_obj.extractText()
    text = re.split(r"\n+", text)
    return [t.strip() for t in text]


def parse_page(
    page_obj: PyPDF2.PageObject,
) -> Tuple[List[str], Tuple[str, str, str, str]]:
    """Parses a page from a PDF, extracting a list of grade data for each section.

    Args:
        page_obj: A PyPDF2.pdf.PageObject representing the current page
    Returns:
        A list of GradeData (see type definition at the top of the file).
    """
    text = sanitize_page(page_obj)
    i = 0
    grade_data = []
    old_pdf_style = False
    while i < len(text):
        if is_header_row(text[i]):
            i += LEN_HEADER_ROW
        elif is_old_header_row(text[i]):
            i += LEN_OLD_HEADER_ROW
            old_pdf_style = True
        elif is_course_total_row(text[i]):
            i += LEN_COURSE_TOTAL_ROW
        elif is_dept_total_row(text[i]):
            i += LEN_DEPT_TOTAL_ROW
        elif is_college_total_row(text[i]):
            i += LEN_COLLEGE_TOTAL_ROW
        else:
            section_row: List[str] = text[slice(i, i + LEN_SECTION_ROW)]
            try:
                dept, course_num, section_num = section_row[0].split("-")
                instructor_name = section_row[-1]
                abcdf_slice = slice(1, 10, 2)
                isuqx_slice = slice(13, 18)
                if old_pdf_style:
                    instructor_name = section_row[2]
                    abcdf_slice = slice(4, 9)
                    isuqx_slice = slice(10, 15)
                letter_grades: List[str] = section_row[abcdf_slice] + section_row[
                    isuqx_slice
                ]
                grade_data.append(
                    (letter_grades, (dept, course_num, section_num, instructor_name))
                )

                i += LEN_SECTION_ROW
            except ValueError:
                i += LEN_SECTION_ROW - 1
    return grade_data


def parse_pdf(pdf_path: str) -> List[Tuple[List[str], Tuple[str, str, str, str]]]:
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        pdf_data = []
        for i in range(pdf_reader.getNumPages()):
            page_data = parse_page(pdf_reader.getPage(i))
            for letter_grades, section_tuple in page_data:
                datatuple = (letter_grades, section_tuple)
                pdf_data.append(datatuple)
        return pdf_data
