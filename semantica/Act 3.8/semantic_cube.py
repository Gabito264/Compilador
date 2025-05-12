semantic_cube = {
    'int': {
        '+':    {'int': 'int',   'float': 'float', 'string': 'error'},
        '-':    {'int': 'int',   'float': 'float', 'string': 'error'},
        '*':    {'int': 'int',   'float': 'float', 'string': 'error'},
        '/':    {'int': 'float', 'float': 'float', 'string': 'error'},
        '<':    {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '>':    {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '<=':   {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '>=':   {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '==':   {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '!=':   {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '=':    {'int': 'int',   'float': 'error', 'string': 'error'}
    },
    'float': {
        '+':    {'int': 'float', 'float': 'float', 'string': 'error'},
        '-':    {'int': 'float', 'float': 'float', 'string': 'error'},
        '*':    {'int': 'float', 'float': 'float', 'string': 'error'},
        '/':    {'int': 'float', 'float': 'float', 'string': 'error'},
        '<':    {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '>':    {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '<=':   {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '>=':   {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '==':   {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '!=':   {'int': 'bool',  'float': 'bool',  'string': 'error'},
        '=':    {'int': 'error', 'float': 'float', 'string': 'error'}
    },
    'string': {
        '+':    {'string': 'string', 'int': 'error', 'float': 'error'},
        '-':    {'string': 'error',  'int': 'error', 'float': 'error'},
        '*':    {'string': 'error',  'int': 'error', 'float': 'error'},
        '/':    {'string': 'error',  'int': 'error', 'float': 'error'},
        '<':    {'string': 'error',  'int': 'error', 'float': 'error'},
        '>':    {'string': 'error',  'int': 'error', 'float': 'error'},
        '<=':   {'string': 'error',  'int': 'error', 'float': 'error'},
        '>=':   {'string': 'error',  'int': 'error', 'float': 'error'},
        '==':   {'string': 'bool',   'int': 'error', 'float': 'error'},
        '!=':   {'string': 'bool',   'int': 'error', 'float': 'error'},
        '=':    {'string': 'string', 'int': 'error', 'float': 'error'}
    }
}