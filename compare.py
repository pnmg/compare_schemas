import compare_schemas
from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-d', '--db', dest="db", action="store", default="mysql")
    parser.add_option('-v', '--verbose', dest="verbose", action="store_true", default=False)
    (opts, args) = parser.parse_args()
    results = compare_schemas.compare(args[0], args[1], options=opts)
    print results