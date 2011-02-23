# Compare Database Schemas

This script helps determine the differences between two database schema files. Currently only supports MySQL schemas. For instance, you can use this to compare databases between Production and Development to see what changes you need to make to either environment.

The process is still pretty raw, but works well in our tests.

## To use via command line:

1. Run `mysqldump --no-data` on your databases you want to compare and save the resulting files.
2. Run `python compare.py file1 file2`

As an example, run:

    python compare.py samples/schema_a.sql samples/schema_b.sql

Output:

    Missing tables: 1; Missing fields: 1

    File 1 missing tables:
    [no missing tables]

    File 1 missing fields:
    [no missing fields]


    File 2 missing tables:
    - C

    File 2 missing fields:
    - B.missingField

## Usage via python

    import compare_schemas
    
    if __name__ == '__main__':
        results = compare_schemas.compare('file1.sql', 'file2.sql')
        # compile our results
        results.report()
        # report
        if results.missing_tables == 0 and results.missing_fields == 0:
            print "Schemas are the same"
        else:
            """
            You can also access the pieces of the results via:
        
            results.file1_missing_elements['tables']
            results.file1_missing_elements['fields']
            results.file2_missing_elements['tables']
            results.file2_missing_elements['fields']
            
            Here we'll just use the built-in reporting
            """
            print results

# License

Copyright (c) 2011 PNMG, Inc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.