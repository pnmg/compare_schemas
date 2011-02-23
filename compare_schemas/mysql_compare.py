"""
MySQL Schema Reader

Defines the REGEXP used for finding pieces of the schema and
how to read the pertinent lines of the schema files.
"""
class MysqlReader(object):
    table_pattern = r'CREATE TABLE `?([^`]+)`?'
    field_pattern = r'^`?([^`\s]+)`?'
    
    def is_constraint(self, line):
        """
        Determine if the line matches a "constraint". Currently constraints are ignored in comparsions
        """
        constraints = ['PRIMARY', 'KEY', 'UNIQUE', 'CONSTRAINT']
        for constraint in constraints:
            if line.startswith(constraint): return True
        return False
    
    def lines_without_comments(self, data):
        return [line.strip() for line in data if not line.startswith('--') and not line.startswith('/*')]