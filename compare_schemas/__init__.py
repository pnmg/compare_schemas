"""
Script to compare two database schema files

Todo:
- Capture field configuration so that we can possible create the alter statements
  as needed
- Capture raw create tables in case we need to use those to create new tables
- Document compare procedure
"""
import os
import re
import sys
from optparse import OptionParser
from mysql_compare import MysqlReader

class SchemaResults(object):
    """
    The result set of a comparison. This primarily consists
    of a list of MissingTable and MissingField objects
    """
    
    def __init__(self, file1, file2):
        """
        Initalize the object with the names of file1 and file2. It's important to store
        these here so that we create summary or perform actions on the results set, we know
        which file is being compared.
        """
        self.results = []
        self.file1 = file1
        self.file2 = file2
    
    def add(self, result):
        """
        Add a result object to the stack
        """
        self.results.append(result)
    
    def report(self):
        self.missing_fields = 0
        self.missing_tables = 0
        self.file1_missing_elements = {'fields':[], 'tables':[]}
        self.file2_missing_elements = {'fields':[], 'tables':[]}
        for result in self.results:
            if isinstance(result, MissingField):
                self.missing_fields += 1
                if result.db == self.file1:
                    self.file1_missing_elements['fields'].append(result)
                else:
                    self.file2_missing_elements['fields'].append(result)
            elif isinstance(result, MissingTable):
                self.missing_tables += 1
                if result.db == self.file1:
                    self.file1_missing_elements['tables'].append(result)
                else:
                    self.file2_missing_elements['tables'].append(result)
        
        self.file1_missing_elements['fields'].sort()
        self.file1_missing_elements['tables'].sort()
        self.file2_missing_elements['fields'].sort()
        self.file2_missing_elements['tables'].sort()
    
    def __str__(self):
        """
        Create a summary of the comparison
        """
        self.report()
        s = "Missing tables: %d; Missing fields: %d\n\n" % (self.missing_tables, self.missing_fields)
        s = "%sFile 1 missing tables:\n" % s
        if len(self.file1_missing_elements['tables']):
            for table in self.file1_missing_elements['tables']:
                s = "%s- %s\n" % (s, table)
        else:
            s = "%s[no missing tables]\n" % s
        
        s = "%s\nFile 1 missing fields:\n" % s
        if len(self.file1_missing_elements['fields']):
            for field in self.file1_missing_elements['fields']:
                s = "%s- %s\n" % (s, field)
        else:
            s = "%s[no missing fields]\n" % s
        
        s = "%s\n\nFile 2 missing tables:\n" % s
        if len(self.file2_missing_elements['tables']):
            for table in self.file2_missing_elements['tables']:
                s = "%s- %s\n" % (s, table)
        else:
            s = "%s[no missing tables]\n" % s
        
        s = "%s\nFile 2 missing fields:\n" % s
        if len(self.file2_missing_elements['fields']):
            for field in self.file2_missing_elements['fields']:
                s = "%s- %s\n" % (s, field)
        else:
            s = "%s[no missing fields]\n" % s
        
        return s


class MissingTable(object):
    """
    Define a table that is missing from the database schema
    """
    def __init__(self, db, table):
        self.db = db
        self.table = table
    
    def __cmp__(self, other):
        if self.table < other.table: return -1
        elif self.table > other.table: return 1
        return 0
    
    def __str__(self):
        return self.table

class MissingField(MissingTable):
    """
    Define a missing field
    """
    def __init__(self, db, table, field, definition=None):
        super(MissingField, self).__init__(db, table)
        self.field = field
        self.definition = definition
    
    def __cmp__(self, other):
        value = super(MissingField, self).__cmp__(other)
        if value != 0: return value
        if self.field < other.field: return -1
        elif self.field > other.field: return 1
        return 0
    
    def __str__(self):
        return "%s.%s" % (self.table, self.field)

def compare(file1, file2, **options):
    """
    Compare schema1 and schema2
    """
    opts = {'db': 'mysql', 'verbose': False}
    if getattr(options['options'], "has_key", None):
        print 1
        opts.update(options['options'])
    else:
        options = vars(options['options'])
        opts.update(options)
    options = opts
    
    results = SchemaResults(file1, file2)
    if os.path.exists(file1) and os.path.exists(file2):
        if options['verbose']: print "Comparing files..."
        filename1 = file1
        filename2 = file2
        if options['verbose']: print "File 1: %s" % file1
        file1 = parse_file(file1, options)
        if options['verbose']: print "File 2: %s" % file2
        file2 = parse_file(file2, options)
    else:
        if options['verbose']: print "Comparing strings..."
        filename1 = "file1"
        filename2 = "file2"
        if options['verbose']: print "File 1"
        file1 = parse_string(file1, options)
        if options['verbose']: print "File 2"
        file2 = parse_string(file2, options)
    
    if options['verbose']:
        print "File 1 Tables: %s" % file1['tables'].keys()
        print "File 2 Tables: %s" % file2['tables'].keys()
    
    # compare tables found in file1 with file2
    tables = file1['tables'].keys()
    tables.sort()
    for table in tables:
        # check if the table exists in file2
        if file2['tables'].has_key(table):
            missing = False
            if options['verbose']: print "File 1, Table %s: %s" % (table, file1['tables'][table])
            for field in file1['tables'][table]:
                try:
                    file2['tables'][table].index(field)
                except ValueError, e:
                    results.add(MissingField(filename2, table, field))
                    if options['verbose']: print "File 2 missing field: %s.%s" % (table, field)
                    missing = True
            
            for field in file2['tables'][table]:
                try:
                    file1['tables'][table].index(field)
                except ValueError, e:
                    if options['verbose']: print "File 1 missing field: %s.%s" % (table, field)
                    results.add(MissingField(filename1, table, field))
                    missing = True
            
            if not missing:
                # print "\tTables match"
                pass
        else:
            # table does not exist in the file2
            results.add(MissingTable(filename2, table))
            if options['verbose']: print "File 2 missing table: %s" % table
    
    # find tables that only in db 2, since they would not have been compared above
    tables_only_db_2 = [table for table in file2['tables'].keys() if not file1['tables'].has_key(table)]
    for table in tables_only_db_2:
        results.add(MissingTable(filename1, table))
        if options['verbose']: print "File 1 missing table: %s" % table
    return results

def parse_file(somefile, options={}):
    """
    Parse the schema file into our table structure
    """
    data = open(somefile, 'r').readlines()
    return parse_string(data, options)

def parse_string(data, options={}):
    """
    Parse the schema file into our table data structure
    """
    opts = {'db':'mysql', 'verbose':False}
    opts.update(options)
    options = opts
    
    reader_name = "%sReader" % options['db'].title()
    reader = globals()[reader_name]
    reader = reader()
    
    if not getattr(data, "append", None):
        data = data.splitlines()
    data = reader.lines_without_comments(data)
    file_data = {'data': data, 'tables':{}}
    
    # regex for matching if the line is a create table object
    is_table = re.compile(reader.table_pattern)
    
    # regex for matching the field name from a schema line
    field_name = re.compile(reader.field_pattern)
    
    # flag for determining if we are in a file
    in_table = False
    # current table name
    table = ''
    
    # parse the file, line-by-line
    for line in data:
        match = is_table.match(line)
        if match:
            # starting a table
            file_data['tables'][match.group(1)] = []
            if options['verbose']: print "Found table %s" % match.group(1)
            in_table = True
            table = match.group(1)
        elif in_table and not line.strip().endswith(','):
            # ending a table
            match = field_name.match(line)
            if match:
                file_data['tables'][table].append(match.group(1))
                if options['verbose']: print "Found table field %s.%s" % (table, match.group(1))
            elif options['verbose']:
                print "Missed line: [%s]" % line
            in_table = False
            table = ''
        elif in_table and not reader.is_constraint(line):
            # found a field line
            match = field_name.match(line)
            if match:
                file_data['tables'][table].append(match.group(1))
                if options['verbose']: print "Found table field %s.%s" % (table, match.group(1))
            elif options['verbose']:
                print "Missed line: [%s]" % line
        elif options['verbose']:
            print "Missed line (all): [%s]" % line
    
    return file_data

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-d', '--db', dest="db", action="store", default="mysql")
    (opts, args) = parser.parse_args()
    results = compare(args[0], args[1], options=opts)
    print results