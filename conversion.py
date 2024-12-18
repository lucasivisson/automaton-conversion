import os
import re

def parse_automaton(file_path):
  # open and close file after scope
  with open(file_path, 'r') as file:
    # transform each line in array
    lines = file.read().splitlines()
  automaton = {}
  # creates an array to state and symbols values
  automaton['states'] = re.findall(r'\b\w+\b', lines[0].split('=')[1])
  automaton['symbols'] = re.findall(r'\b\w+\b', lines[1].split('=')[1])
  transitions = {}
  for line in lines[2:]:
    #   continue
    # verify if each transition is in (qx, 0) -> qy pattern
    match = re.match(r'\((\w+), (\w+)\) -> (.+)', line.strip())
    if match:
      # separate each state and symbol
      current, symbol, next_state = match.groups()
      # split next states by comma and strip any whitespace
      next_states_list = [state.strip() for state in next_state.split(',')]
      # add transition to transitions dict
      for next_state in next_states_list:
        transitions.setdefault((current, symbol), []).append(next_state) 
      # transitions.setdefault((current, symbol), []).append(next_states_list)
  automaton['transitions'] = transitions
  # add start_state to automaton
  automaton['start_state'] = lines[-3].split('=')[1].strip()
  # add final_states to automaton
  automaton['final_states'] = re.findall(r'\b\w+\b', lines[-2].split('=')[1])

  word_line = next(line for line in lines if line.startswith("w ="))
  automaton['input_string'] = word_line.split("=")[1].strip()
  return automaton

def build_e_closure(automaton):
  e_closures= {}
  for state in automaton['states']:
    # get state returned by void transitions
    e_closure_states = automaton['transitions'].get((state, 'vazio'), [])
    # add self state to e_closure
    e_closures[state] = [state]
    if len(e_closure_states) != 0:
      # add each state returned by void transitions to e_closure
      e_closures[state].extend(e_closure_states)
  return e_closures

def build_afd(automaton, e_closures):
  start_state = tuple(e_closures[automaton['start_state']])  # Estado inicial do AFD
  afd_states = {start_state}  # AFD state
  afd_transitions = {}  # AFD transitions
  unprocessed_states = [start_state]  # pending process states
  afd_final_states = []  # final AFD states

  # process afd states
  while unprocessed_states:
    current_state = unprocessed_states.pop(0)  # current unprocessed state
    
    for symbol in automaton['symbols']:
      if symbol == 'vazio':  # ignore void transitions
        continue

      # find and save reachable states by symbol
      reachable = set()
      for sub_state in current_state:
        reachable.update(automaton['transitions'].get((sub_state, symbol), []))

      # calculate e-closure of reachable state
      e_closure_reachable = set()
      for state in reachable:
        e_closure_reachable.update(e_closures[state])

      e_closure_tuple = tuple(sorted(e_closure_reachable))

      # register a new state if state is not inside afd_states and add new state to unprocessed_states to be processed on next loop
      if e_closure_tuple not in afd_states:
        afd_states.add(e_closure_tuple)
        unprocessed_states.append(e_closure_tuple)

      # register transition on AFD
      afd_transitions[(current_state, symbol)] = e_closure_tuple

  # identify final states on AFD
  for afd_state in afd_states:
    # Is a final state if final AFN state is in any of AFD state 
    if any(state in automaton['final_states'] for state in afd_state):
      afd_final_states.append(afd_state)

  symbols = [symbol for symbol in automaton['symbols'] if symbol != 'vazio']
  
  # return AFD
  return {
    'states': list(afd_states),
    'symbols': symbols,
    'transitions': afd_transitions,
    'start_state': start_state,
    'final_states': afd_final_states,
  }

def build_afd_complement(afd):
  afd_final_states = []
  for state in afd['states']:
    if state not in afd['final_states']:
      afd_final_states.append(state)
  
  return {
    'states': afd['states'],
    'symbols': afd['symbols'],
    'transitions': afd['transitions'],
    'start_state': afd['start_state'],
    'final_states': afd_final_states,
  }

def create_afd_with_one_final_state(afd):
  new_final_state = tuple(['qf'])
  states = set(afd['states'])
  states.add(new_final_state)

  afd_transitions = {}
  afd_transitions.update(afd['transitions'])

  for final_state in afd['final_states']:
    afd_transitions[(final_state, 'vazio')] = 'qf'

  return {
    'states': list(states),
    'symbols': afd['symbols'],
    'transitions': afd_transitions,
    'start_state': afd['start_state'],
    'final_states': new_final_state,
  }

def build_reverse_afd(af):
  if len(af['final_states']) > 1:
    afn_with_one_final_state = create_afd_with_one_final_state(af)
  if afn_with_one_final_state:
    af = afn_with_one_final_state

  af_transitions = {}
  for (state, symbol), next_state in af['transitions'].items():
    af_transitions.setdefault((next_state, symbol), []).append(state)

  return {
    'states': af['states'],
    'symbols': af['symbols'],
    'transitions': af_transitions,
    'start_state': af['final_states'],
    'final_states': [af['start_state']],
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
            file.write(f"transitions = {{\n")
            for (state, symbol), next_state in automaton['transitions'].items():
                if symbol == 'vazio':
                    file.write(f"({state}, vazio) -> {next_state}\n")
                else:
                    file.write(f"({state}, {symbol}) -> {next_state}\n")
            file.write(f"}}\n")
            file.write(f"start_state = {automaton['start_state']}\n")
            file.write(f"final_states = {automaton['final_states']}\n")
            
            if include_input_string:
                file.write(f"w = {automaton['input_string']}\n")
            
        print(f"Arquivo salvo: {full_file_path}")
    
    except Exception as e:
        print(f"Erro ao salvar o arquivo {file_name}: {e}")

automaton = parse_automaton('AFN.txt')
e_closures = build_e_closure(automaton)
afd = build_afd(automaton, e_closures)
afd_complement = build_afd_complement(afd)
reverse_afd = build_reverse_afd(afd)

save_automaton_to_file(afd, "AFD.txt", include_input_string=False)
save_automaton_to_file(afd_complement, "COMP.txt", include_input_string=False)
save_automaton_to_file(reverse_afd, "REV.txt", include_input_string=False)

input_string = automaton['input_string']
is_accepted_afd = simulate_afd(afd, input_string)
is_accepted_complement = simulate_afd(afd_complement, input_string)
is_accepted_reverse = simulate_afd(reverse_afd, input_string)
print(f"A cadeia '{input_string}' foi {'ACEITA' if is_accepted_afd else 'REJEITADA'} pelo AFD.")
print(f"A cadeia '{input_string}' foi {'ACEITA' if is_accepted_complement else 'REJEITADA'} pelo Complemento do AFD.")
print(f"A cadeia '{input_string}' foi {'ACEITA' if is_accepted_reverse else 'REJEITADA'} pelo Reverso do AFD.")