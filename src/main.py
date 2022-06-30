import csv
import os
from concurrent.futures import ProcessPoolExecutor
import pathlib
import re
from typing import Dict, List, Tuple

import bs4
import requests
import urllib3
from requests import Response
import pandas as pd

import pdf_parser

urllib3.disable_warnings()

ROOT_URL = "https://web-as.tamu.edu/GradeReports/"
PDF_URL = "https://web-as.tamu.edu/GradeReports/PDFReports/{}/grd{}{}.pdf"
PDF_DOWNLOAD_DIR = os.path.abspath("documents/pdfs")

SPRING, SUMMER, FALL = "1", "2", "3"
QATAR = "QT"
GALVESTON = "GV"


def years() -> List[int]:
    """
    Scrapes all of the years listed on the TAMU grade distribution site.
    """
    response: Response = requests.get(ROOT_URL, verify=False)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.text, "lxml")
    options = soup.select("#ctl00_plcMain_lstGradYear > option")
    return [int(o["value"]) for o in options]


def colleges() -> List[str]:
    """
    Scrapes all of the colleges offered on the TAMU grade distribution site.
    """
    response: Response = requests.get(ROOT_URL, verify=False)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.text, "lxml")
    options = soup.select("#ctl00_plcMain_lstGradCollege > option")
    return [o["value"] for o in options]


def download_pdf(args: Tuple[str, str]) -> str:
    """Downloads a PDF from the given URL.

    Args:
        args: A tuple containing the year_semester (just the year concatenated with the semester) and the college.
    Returns:
        The path to the downloaded PDF file.
    """
    year_semester, college = args
    url = PDF_URL.format(year_semester, year_semester, college)
    filename = url.split("/")[-1]
    path = os.path.join(PDF_DOWNLOAD_DIR, filename)
    if os.path.isfile(path):
        return path
    response = requests.get(url, verify=False)
    try:
        response.raise_for_status()
        print(year_semester, college)
        with open(path, "wb+") as file:
            file.write(response.content)
            return path
    except requests.exceptions.HTTPError as error:
        if error.response.status_code != 404:
            raise error


def get_files_in_dir(directory: str, extension: str) -> List[str]:
    abspaths = []
    for file in os.listdir(directory):
        if file.endswith(extension):
            abspaths.append(os.path.join(os.path.abspath(directory), file))
    return abspaths


def parse_csvs():
    yrs = years()
    print(yrs)
    college_abbrevs = colleges()
    arguments = []
    for year in yrs:
        for semester in [SPRING, SUMMER, FALL]:
            year_semester = str(year) + semester
            for college in college_abbrevs:
                arguments.append((year_semester, college))
    with ProcessPoolExecutor() as executor:
        executor.map(download_pdf, arguments)
        pdf_paths = get_files_in_dir(PDF_DOWNLOAD_DIR, ".pdf")
        for pdf_path in pdf_paths:
            if not pdf_path:
                continue
            distribution_fields = pdf_parser.parse_pdf(pdf_path)
            with open(pdf_path.replace(".pdf", ".csv"), "w+") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [
                        "A",
                        "B",
                        "C",
                        "D",
                        "F",
                        "I",
                        "S",
                        "U",
                        "Q",
                        "X",
                        "DEPT",
                        "COURSE_NUM",
                        "SECTION_NUM",
                        "INSTRUCTOR_NAME",
                    ]
                )
                for dist in distribution_fields:
                    (
                        grades,
                        (dept, course_num, section_num, instructor_name),
                    ) = dist
                    writer.writerow(
                        [*grades, dept, course_num, section_num, instructor_name]
                    )


def grd_to_term_code(grd: str) -> str:
    try:
        [(year, semester, college)] = re.findall(
            "grd(?P<year>\d{4})(?P<semester>\d)(?P<college>[\w\_]+)", grd
        )
        if college == "GV":
            return year + semester + "2"
        if college == "QT":
            return year + semester + "3"
        return year + semester + "1"
    except Exception as e:
        print(grd)
        raise e


def concat_csvs():
    paths = sorted(
        [
            pathlib.Path(abspath)
            for abspath in get_files_in_dir(PDF_DOWNLOAD_DIR, ".csv")
        ]
    )
    dataframes: Dict[str, pd.DataFrame] = {}
    for path in paths:
        term_code = grd_to_term_code(str(path))
        df = pd.read_csv(path)
        if term_code not in dataframes:
            dataframes[term_code] = df
        else:
            dataframes[term_code] = pd.concat([dataframes[term_code], df])
    for key, val in dataframes.items():
        val.to_csv(os.path.join("documents", "csvs", f"{key}.csv"))


def main():
    parse_csvs()
    concat_csvs()


if __name__ == "__main__":
    main()

# https://web-as.tamu.edu/gradereport/PDFReports/20211/grd20211EN.pdf
# https://web-as.tamu.edu/GradeReports/PDFReports/20211/grd20211EN.pdf
