
#Revisar las entradas válidas y de error del cubo semántico
semantic_cube = {
    'int': {
        '+':    {'int': 'int',   'float': 'float', 'string': 'error', 'error': 'error', '':'int', 'bool': 'error'},
        '-':    {'int': 'int',   'float': 'float', 'string': 'error', 'error': 'error', '':'int', 'bool': 'error'},
        '*':    {'int': 'int',   'float': 'float', 'string': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '/':    {'int': 'float', 'float': 'float', 'string': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '<':    {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error', '':'error', 'bool': 'bool'},
        '>':    {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error', '':'error', 'bool': 'bool'},
        '<=':   {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error', '':'error', 'bool': 'bool'},
        '>=':   {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error','':'error', 'bool': 'bool'},
        '==':   {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error', '':'error', 'bool': 'bool'},
        '!=':   {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error','':'error', 'bool': 'bool'},
        '=':    {'int': 'int',   'float': 'error', 'string': 'error', 'error': 'error','':'error', 'bool': 'error'}
    },
    'float': {
        '+':    {'int': 'float', 'float': 'float', 'string': 'error', 'error': 'error', '':'float', 'bool': 'error'},
        '-':    {'int': 'float', 'float': 'float', 'string': 'error', 'error': 'error', '': 'float', 'bool': 'error'},
        '*':    {'int': 'float', 'float': 'float', 'string': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '/':    {'int': 'float', 'float': 'float', 'string': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '<':    {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error', '':'error', 'bool': 'bool'},
        '>':    {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error', '':'error', 'bool': 'bool'},
        '<=':   {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error', '':'error', 'bool': 'bool'},
        '>=':   {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error', '':'error', 'bool': 'bool'},
        '==':   {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error', '':'error', 'bool': 'bool'},
        '!=':   {'int': 'bool',  'float': 'bool',  'string': 'error', 'error': 'error', '':'error', 'bool': 'bool'},
        '=':    {'int': 'error', 'float': 'float', 'string': 'error', 'error': 'error', '':'error', 'bool': 'error'}
    },
    'string': {
        '+':    {'string': 'string', 'int': 'error', 'float': 'error', 'error': 'error', '':'error'},
        '-':    {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error'},
        '*':    {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error'},
        '/':    {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error'},
        '<':    {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error'},
        '>':    {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error'},
        '<=':   {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error'},
        '>=':   {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error'},
        '==':   {'string': 'bool',   'int': 'error', 'float': 'error', 'error': 'error', '':'error'},
        '!=':   {'string': 'bool',   'int': 'error', 'float': 'error', 'error': 'error', '':'error'},
        '=':    {'string': 'string', 'int': 'error', 'float': 'error', 'error': 'error', '':'error'}
    },
    'error':{
        '+':    {'string': 'error', 'int': 'error', 'float': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '-':    {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '*':    {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '/':    {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '<':    {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '>':    {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '<=':   {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '>=':   {'string': 'error',  'int': 'error', 'float': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '==':   {'string': 'error',   'int': 'error', 'float': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '!=':   {'string': 'error',   'int': 'error', 'float': 'error', 'error': 'error', '':'error', 'bool': 'error'},
        '=':    {'string': 'error', 'int': 'error', 'float': 'error', 'error': 'error', '':'error', 'bool': 'error'}
    }
}