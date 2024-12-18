import os
import re

def parse_automaton(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()

    automaton = {}
    automaton['states'] = re.findall(r'\b\w+\b', lines[0].split('=')[1])
    automaton['symbols'] = re.findall(r'\b\w+\b', lines[1].split('=')[1])

    transitions = {}
    for line in lines[2:]:
        if line.startswith("q") or line.startswith("F") or line.startswith("w"):
            break
        match = re.match(r'\((\w+), (\w+)\) -> (\w+)', line.strip())
        if match:
            current, symbol, next_state = match.groups()
            transitions.setdefault((current, symbol), []).append(next_state)
    automaton['transitions'] = transitions

    initial_line = next(line for line in lines if ": inicial" in line)
    automaton['start_state'] = initial_line.split(":")[0].strip()

    final_line = next(line for line in lines if line.startswith("F:"))
    automaton['final_states'] = re.findall(r'\b\w+\b', final_line.split(":")[1])

    word_line = next(line for line in lines if line.startswith("w:"))
    automaton['input_string'] = word_line.split(":")[1].strip()

    return automaton

def build_e_closure(automaton):
    e_closures = {}
    for state in automaton['states']:
        e_closure_states = automaton['transitions'].get((state, 'vazio'), [])
        e_closures[state] = [state] + e_closure_states
    return e_closures

def build_afd(automaton, e_closures):
    start_state = tuple(e_closures[automaton['start_state']])
    afd_states = {start_state}
    afd_transitions = {}
    unprocessed_states = [start_state]
    afd_final_states = []

    while unprocessed_states:
        current_state = unprocessed_states.pop(0)
        for symbol in automaton['symbols']:
            reachable = set()
            for sub_state in current_state:
                reachable.update(automaton['transitions'].get((sub_state, symbol), []))
            e_closure_reachable = set()
            for state in reachable:
                e_closure_reachable.update(e_closures[state])
            e_closure_tuple = tuple(sorted(e_closure_reachable))
            if e_closure_tuple not in afd_states:
                afd_states.add(e_closure_tuple)
                unprocessed_states.append(e_closure_tuple)
            afd_transitions[(current_state, symbol)] = e_closure_tuple

    for afd_state in afd_states:
        if any(state in automaton['final_states'] for state in afd_state):
            afd_final_states.append(afd_state)

    return {
        'states': list(afd_states),
        'symbols': automaton['symbols'],
        'transitions': afd_transitions,
        'start_state': start_state,
        'final_states': afd_final_states,
    }

def build_afd_complement(afd):
    afd_final_states = [state for state in afd['states'] if state not in afd['final_states']]
    return {
        'states': afd['states'],
        'symbols': afd['symbols'],
        'transitions': afd['transitions'],
        'start_state': afd['start_state'],
        'final_states': afd_final_states,
    }

def build_reverse_afd(afd):
    reverse_transitions = {}
    for (state, symbol), next_state in afd['transitions'].items():
        reverse_transitions.setdefault((next_state, symbol), []).append(state)

    reverse_final_states = [afd['start_state']]
    reverse_start_state = tuple(afd['final_states'])

    return {
        'states': afd['states'],
        'symbols': afd['symbols'],
        'transitions': reverse_transitions,
        'start_state': reverse_start_state,
        'final_states': reverse_final_states,
    }

def simulate_afd(afd, input_string):
    current_state = afd['start_state']
    for symbol in input_string:
        transition_key = (current_state, symbol)
        if transition_key in afd['transitions']:
            current_state = afd['transitions'][transition_key]
        else:
            return False
    return current_state in afd['final_states']

def save_automaton_to_file(automaton, file_name, include_input_string=True):
    try:
        dir_path = os.path.dirname(os.path.abspath(__file__))
        full_file_path = os.path.join(dir_path, file_name)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(full_file_path, 'w', encoding='utf-8') as file:
            file.write(f"states = {', '.join(str(state) for state in automaton['states'])}\n")
            file.write(f"symbols = {', '.join(str(symbol) for symbol in automaton['symbols'])}\n")
            
            for (state, symbol), next_state in automaton['transitions'].items():
                if symbol == 'vazio':
                    file.write(f"({state}, vazio) -> {', '.join(str(s) for s in next_state)}\n")
                else:
                    file.write(f"({state}, {symbol}) -> {', '.join(str(s) for s in next_state)}\n")
            
            file.write(f"{automaton['start_state']}: inicial\n")
            file.write(f"F: {', '.join(str(state) for state in automaton['final_states'])}\n")
            
            if include_input_string:
                file.write(f"w: {automaton['input_string']}\n")
            
        print(f"Arquivo salvo: {full_file_path}")
    
    except Exception as e:
        print(f"Erro ao salvar o arquivo {file_name}: {e}")

input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "afn.txt")
automaton = parse_automaton(input_file)
e_closures = build_e_closure(automaton)
afd = build_afd(automaton, e_closures)
afd_complement = build_afd_complement(afd)
reverse_afd = build_reverse_afd(afd)

save_automaton_to_file(automaton, "AFN Original.txt", include_input_string=True)
save_automaton_to_file(afd, "AFD.txt", include_input_string=False)
save_automaton_to_file(afd_complement, "COMP.txt", include_input_string=False)
save_automaton_to_file(reverse_afd, "REV.txt", include_input_string=False)

input_string = automaton['input_string']
is_accepted = simulate_afd(afd, input_string)
print(f"A cadeia '{input_string}' foi {'ACEITA' if is_accepted else 'REJEITADA'} pelo AFD.")