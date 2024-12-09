import re

def parse_automaton(file_path):
  with open(file_path, 'r') as file:
      lines = file.read().splitlines()

  automaton = {}
  automaton['states'] = re.findall(r'\b\w+\b', lines[0].split('=')[1])
  automaton['symbols'] = re.findall(r'\b\w+\b', lines[1].split('=')[1])

  transitions = {}
  for line in lines[2:]:
      if line.startswith("transitions"):
          continue
      match = re.match(r'\((\w+), (\w+)\) -> (\w+)', line.strip())
      if match:
          current, symbol, next_state = match.groups()
          transitions.setdefault((current, symbol), []).append(next_state)
  automaton['transitions'] = transitions

  automaton['start_state'] = lines[-2].split('=')[1].strip()
  automaton['final_states'] = re.findall(r'\b\w+\b', lines[-1].split('=')[1])

  return automaton

def build_e_closure(automaton):
  e_closures= {}
  for state in automaton['states']:
    e_closure_states = automaton['transitions'].get((state, 'vazio'), [])
    e_closures[state] = [state]
    if len(e_closure_states) != 0:
      e_closures[state].extend(e_closure_states)
  return e_closures      

automaton = parse_automaton('afn.txt')
print(build_e_closure(automaton))
print(automaton)

