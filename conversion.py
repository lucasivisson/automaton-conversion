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
  # Create an empty list to store the final states of the complement AFD
  afd_final_states = []
  # If the state is not in the final states of the original AFD, add it to the complement's final states
  for state in afd['states']:
    if state not in afd['final_states']:
      afd_final_states.append(state)
  
  # Return a new AFD with the same states, symbols, and transitions,
  # but with the final states replaced by the complement of the original final states
  return {
    'states': afd['states'],
    'symbols': afd['symbols'],
    'transitions': afd['transitions'],
    'start_state': afd['start_state'],
    'final_states': afd_final_states,
  }

def create_afd_with_one_final_state(afd):
  # Create a new final state called 'qf' (a unique state representing the single final state)
  new_final_state = tuple(['qf'])

  # Add the new final state to the set of states in the AFD
  states = set(afd['states'])
  states.add(new_final_state)

  # Create a copy of the AFD's transitions
  afd_transitions = {}
  afd_transitions.update(afd['transitions'])

  # For each final state in the original AFD, add a transition from the final state to the new final state with epsilon
  for final_state in afd['final_states']:
    afd_transitions[(final_state, 'vazio')] = new_final_state

  # Return a new AFD with the new final state and updated transitions
  return {
    'states': list(states),
    'symbols': afd['symbols'],
    'transitions': afd_transitions,
    'start_state': afd['start_state'],
    'final_states': new_final_state,
  }

def build_reverse_afd(af):
  # Check if there are multiple final states, and if so, convert the AFD to an AFN with one final state
  if len(af['final_states']) > 1:
    af = create_afd_with_one_final_state(af)

  # Create an empty dictionary to store the reversed transitions
  af_transitions = {}
  # Loop through each transition in the original AFD, reversing the direction
  for (state, symbol), next_state in af['transitions'].items():
    # Reverse the transition by swapping the state and next_state
    af_transitions.setdefault((next_state, symbol), []).append(state)

  # Return the reversed AFD
  return {
    'states': af['states'],
    'symbols': af['symbols'],
    'transitions': af_transitions,
    'start_state': af['final_states'],
    'final_states': [af['start_state']],
  }
  
def simulate_afd(af, input_string):
    # Set the initial state to the start state of the AFD
    current_state = af['start_state']

    # Process each symbol in the input string
    for symbol in input_string:
        # Create a transition key by pairing the current state and the symbol
        transition_key = (current_state, symbol)

        # Check if a transition exists for the current state and symbol
        if transition_key in af['transitions']:
            # Update the current state to the next state based on the transition
            current_state = af['transitions'][transition_key]
        else:
            return False
        
    # After processing the entire input string, check if the final state is one of the AFD's final states
    return current_state in af['final_states']
       

def save_automaton_to_file(automaton, file_name):
    try:
        # Get the directory path of the current script and build the full file path
        dir_path = os.path.dirname(os.path.abspath(__file__))
        full_file_path = os.path.join(dir_path, file_name)

        # Create the directory if it does not exist
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # Open the file in write mode and save the automaton's details
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
            
        print(f"Arquivo salvo: {full_file_path}")
    
    except Exception as e:
        print(f"Erro ao salvar o arquivo {file_name}: {e}")

automaton = parse_automaton('input.txt')
e_closures = build_e_closure(automaton)
afd = build_afd(automaton, e_closures)
afd_complement = build_afd_complement(afd)
af_reverse = build_reverse_afd(afd)

save_automaton_to_file(afd, "AFD.txt")
save_automaton_to_file(afd_complement, "COMP.txt")
save_automaton_to_file(af_reverse, "REV.txt")

input_afd = '10001'
is_accepted_afd = simulate_afd(afd, input_afd)
print(f"A cadeia '{input_afd}' foi {'ACEITA' if is_accepted_afd else 'REJEITADA'} pelo AFD.")