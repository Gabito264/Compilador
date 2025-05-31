class MemoryManager:
    def __init__(self):
        self.counters = {
            'global_int': 1000,
            'global_float': 2000,
            'global_string': 3000,
            'global_void': 4000,
            'local_int': 7000,
            'local_float': 8000,
            'local_string': 9000,
            'temp_int': 12000,
            'temp_float': 13000,
            'temp_bool': 14000,
            'cte_int': 17000,
            'cte_float': 18000,
            'cte_string': 19000,
        }

    def allocate(self, segment):
        addr = self.counters[segment]
        self.counters[segment] += 1
        return addr

    def get_initial_value(key):
        if key.startswith('global'):
            return {'global_int': 1000, 'global_float': 2000, 'global_string': 3000, 'global_void': 4000}[key]
        elif key.startswith('local'):
            return {'local_int': 7000, 'local_float': 8000, 'local_string': 9000}[key]
        elif key.startswith('temp'):
            return {'temp_int': 12000, 'temp_float': 13000, 'temp_bool': 14000}[key]
        elif key.startswith('cte'):
            return {'cte_int': 17000, 'cte_float': 18000, 'cte_string': 19000}[key]
        return 0

    def add_counters_from(self, other_memory):
        for key in self.counters:
            if key in other_memory.counters:
                self.counters[key] += (other_memory.counters[key] - self.get_initial_value(key))


def get_segment(scope, var_type):
    if scope == "global":
        return f"global_{var_type}"
    elif scope == "local":
        return f"local_{var_type}"
    elif scope == "temp":
        return f"temp_{var_type}"
    elif scope == "cte":
        return f"cte_{var_type}"
    elif scope == "void":
        return "global_void"
    else:
        raise ValueError(f"Scope '{scope}' not supported")


class ConstantTable:
    def __init__(self, memory_manager):
        self.table = {}
        self.memory_manager = memory_manager

    def get_or_add(self, value, var_type):
        if value in self.table:
            return self.table[value]
        addr = self.memory_manager.allocate(get_segment("cte", var_type))
        self.table[value] = addr
        return addr