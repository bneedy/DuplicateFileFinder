import webbrowser
from os import walk
from os.path import getsize, join, basename, dirname, abspath
from time import time, sleep
from lxml import etree
from itertools import zip_longest

class FileFinder(object):
    """Class that will find duplicate files"""

    def __init__(self, paths=[]):
        super(FileFinder, self).__init__()
        self.paths = paths
        self.outputFilePath = r"output.html"
        self.htmlFileOut = ""

        # Flag to run a deep scan analysis as well
        self.deepScan = False

    def openFile(self):
        if self.htmlFileOut != "":
            # Write the html to a file
            with open(self.outputFilePath, 'w') as fp:
                fp.write(self.htmlFileOut)
            # Open the html file in a browser
            webbrowser.open(str(self.outputFilePath));

    def setupOutputFilePath(self, path):
        self.outputFilePath = path

    def declareFileSearchPaths(self, paths):
        self.paths = paths

    def setDeepScanFlag(self, flag):
        self.deepScan = flag

    def run(self):
        self.run(self.paths, None)

    def run(self, paths):
        self.run(paths, None)

    def run(self, paths, funcs):
        # Dictionary of all the files found
        fileDict = {}

        # Duplicate sizes
        duplicateSizes = []

        # Maximum number of duplicates for columns in a table
        maxDups = 0

        htmlInitial = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        table {
            width:100%;
        }
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding: 5px;
            text-align: left;
        }
        table tr:nth-child(even) {
            background-color: #eee;
        }
        table tr:nth-child(odd) {
           background-color:#fff;
        }
        table th {
            background-color: black;
            color: white;
        }
        </style>
        </head>
        <body>

        <h1>Duplicate File Finder</h1>

        """

        htmlBody = ""

        htmlEnd = """
        </table>

        </body>
        </html>
        """

        dirpathlist = []
        for p in paths:
            dirpathlist.append(abspath(p))
        
        startTime = time()

        for path in paths:
            # Perform shallow analysis (file size checks)
            for (dirpath, dirnames, filenames) in walk(path):
                # Ignore exploring paths that are already on the list to be explored
                if dirpath != abspath(path) and abspath(dirpath) in dirpathlist:
                    continue

                for f in filenames:
                    size = getsize(join(dirpath, f))

                    # we have a duplicate file size
                    if size in fileDict:
                        if size not in duplicateSizes:
                            duplicateSizes.append(size)

                        fileDict[size].append(join(dirpath, f))
            
                        # get the maximum number of duplicates for a file
                        count = len(fileDict[size])
                        if count > maxDups:
                            maxDups = count

                    else:
                        fileDict[size] = [join(dirpath, f)]

        # Time taken to perform shallow analysis
        htmlInitial += "<p>Shallow analysis took " + str(round(time() - startTime, 3)) + " seconds.\n</p>"

        # Restart time for deep analysis if needed
        startTime = time()

        if funcs is not None:
            funcs[0](len(duplicateSizes))

        # Create html document and perform deep analysis if needed
        for num, s in enumerate(sorted(duplicateSizes)):
            unique = False
            ignoredNums = []
            #print("Num " + str(num) + " out of " + str(len(duplicateSizes)))
            
            if funcs is not None:
                funcs[1](num+1)

            if self.deepScan:
                for rows in zip_longest(*[open(i, "rb") for i in fileDict[s]]):
                    rows = list(rows)

                    # Remove currently unique items
                    for i in ignoredNums:
                        del rows[i]

                    num = len(set(rows))
                    # if the set = 1 then all are the same, if set is len then all are different
                    # Check it the rows are not the same
                    if num > 1:
                        # All are unique
                        if num == len(rows):
                            unique = True
                            break
                        # Some are still the same
                        else:
                            dups = []
                            for i, v in enumerate(rows):
                                if v in rows[i+1:]:
                                    dups.append(i)
                                    dups.append(i + 1 + rows[i+1:].index(v))
                            for i in range(len(rows)):
                                if i not in set(dups):
                                    ignoredNums.append(i)
                                    del fileDict[s][i]

            # Ignore printing if all files are unique
            if unique:
                continue    

            htmlBody += "  <tr>\n"
            htmlBody += "    <td>" + str(s) + "</td>\n"
    
            i = 0
            for f in fileDict[s]:
                htmlBody += "    <td>" + str(dirname(f)) + "\\<a href=\"file:///" + str(f) + "\">" + str(basename(f)) + "</a></td>\n"
                i += 1

            if i < maxDups:
                for v in range(maxDups - i):
                    htmlBody += "    <td></td>\n"
            htmlBody += "  </tr>\n"

        # Add the deep scan time
        if self.deepScan:
            htmlInitial += "<p>Deep analysis took " + str(round(time() - startTime, 3)) + " seconds.\n</p>"

        # Add the table heading
        htmlInitial += "<table>\n  <tr>\n  <th>File Size (Bytes)</th>\n"
        for num in range(maxDups):
            htmlInitial += "    <th>Duplicate #" + str(num+1) + "</th>\n"
        htmlInitial +=  "  </tr>\n"

        # Combine all the html into a single string
        self.htmlFileOut = htmlInitial + htmlBody + htmlEnd