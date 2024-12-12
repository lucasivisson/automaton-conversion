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
    match = re.match(r'\((\w+), (\w+)\) -> (\w+)', line.strip())
    if match:
      # separate each state and symbol
      current, symbol, next_state = match.groups()
      # add transition to transitions dict
      transitions.setdefault((current, symbol), []).append(next_state)
  automaton['transitions'] = transitions

  # add start_state to automaton
  automaton['start_state'] = lines[-2].split('=')[1].strip()
  # add final_states to automaton
  automaton['final_states'] = re.findall(r'\b\w+\b', lines[-1].split('=')[1])

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

  # return AFD
  return {
    'states': list(afd_states),
    'symbols': automaton['symbols'],
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

  new_symbol = 'vazio'
  symbols = set(afd['symbols'])
  symbols.add(new_symbol)

  afd_transitions = {}
  afd_transitions.update(afd['transitions'])

  for final_state in afd['final_states']:
    afd_transitions[(final_state, new_symbol)] = 'qf'

  return {
    'states': states,
    'symbols': symbols,
    'transitions': afd_transitions,
    'start_state': afd['start_state'],
    'final_states': new_final_state,
  }

def build_reverse_afd(afd):
  if len(afd['final_states']) > 1:
    a = create_afd_with_one_final_state(afd)
    print(a)



automaton = parse_automaton('afn.txt')
e_closures = build_e_closure(automaton)
afd = build_afd(automaton, e_closures)
afd_complement = build_afd_complement(afd)
reverse_afd = build_reverse_afd(afd)
# print('afd_complement', afd_complement)
# print(automaton)
# print(afd)

