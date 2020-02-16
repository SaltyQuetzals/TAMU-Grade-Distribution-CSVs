# pdf-parser
Machine-readable grade distributions are **Good Bull**.
If you wind up using this data or code in some form, credit would be appreciated. 
Just add your name to [`using.md`](using).

# What is it?
This is a simple script designed to:
1. Download TAMU grade distribution PDFs from previous years (they have removed PDFs from before 2014) (using [requests](https://github.com/psf/requests))
2. Extract the data in those PDFs (using [PyPDF2](https://pythonhosted.org/PyPDF2/))
3. Convert that data into CSV format and save it for use in your ML/stats project, scheduling app, or whatever you might need it for.

# How do I use it?
If you'd like to use the data, there will be a [ZIP file published as a release](https://github.com/SaltyQuetzals/pdf-parser/releases) automatically every month that contains all of the scraped CSV data.

If you want the PDFs or CSVS individually, just run (with Python 3 installed)

1. Create a new virtual environment (I use `python3 -m venv env` on Ubuntu 18.04) and activate it (`source env/bin/activate`)
2. Install the dependencies (`pip install -r requirements.txt`)
3. `python main.py`



# Why'd you make it?
Texas A&M University likes to [publish their grade distributions publicly](https://web-as.tamu.edu/gradereport/) for record-keeping. 
The university does not provide access to machine-readable versions of these files without a department head signature and special permission.
I don't want to get either of those things.


# How do I help?
Pull requests of all kinds are welcome!
Some issues I'm trying to tackle:

- [ ] Automating releases to be every 3 months or so using [GitHub Actions](https://github.com/features/actions).
- [ ] Refactoring/cleaning up code
- [ ] Including data from before 2014 ([Marcus Salinas has 2012-2014](https://drive.google.com/drive/folders/0B6WlnfAGiKk9ZlEwcElEZW9rUE0), but I can't find anything from before 2012).
- [ ] Refining data collection
    - [ ] Using instructor's real names, rather than `"LAST, F."`