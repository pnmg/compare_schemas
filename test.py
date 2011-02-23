"""
Test cases for this library
"""
import unittest
import compare_schemas

class BasicSchemaComparisonTestCase(unittest.TestCase):
    def setUp(self):
        self.schema_a = """CREATE TABLE `A` (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        value TEXT NOT NULL
        );
        CREATE TABLE `B` (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        value TEXT NOT NULL,
        missingField TEXT NOT NULL
        );
        CREATE TABLE `C` (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        value TEXT NOT NULL
        );"""
        self.schema_b = """CREATE TABLE `A` (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        value TEXT NOT NULL
        );
        CREATE TABLE `B` (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        value TEXT NOT NULL
        );"""
    
    def testCompare(self):
        results = compare_schemas.compare(self.schema_a, self.schema_b)
        results.report()
        self.failUnlessEqual(results.missing_tables, 1)
        self.failUnlessEqual(results.missing_fields, 1)
        self.failUnlessEqual(results.file2_missing_elements['tables'][0].table, 'C')
        self.failUnlessEqual(results.file2_missing_elements['fields'][0].field, 'missingField')

class CompareSameSchemasTestCase(unittest.TestCase):
    def setUp(self):
        self.schema_a = """CREATE TABLE `A` (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        value TEXT NOT NULL
        );
        CREATE TABLE `B` (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        value TEXT NOT NULL
        );"""
        self.schema_b = """CREATE TABLE `A` (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        value TEXT NOT NULL
        );
        CREATE TABLE `B` (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        value TEXT NOT NULL
        );"""
    
    def testCompare(self):
        results = compare_schemas.compare(self.schema_a, self.schema_b)
        results.report()
        self.failUnlessEqual(results.missing_tables, 0, "There should be no missing tables")
        self.failUnlessEqual(results.missing_fields, 0, "There should be no missing fields: %s" % [result.__str__() for result in results.results])

if __name__ == '__main__':
    unittest.main()