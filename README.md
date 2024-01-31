Batch-curry reads from stdin a YAML list of argument lists and a set of command templates as arguments. It curries the commands with the argument lists, runs them, and captures the outputs, storing them in a new list.

Example:

argument list:
- - hello
  - world
- - brain
  - wash

template filters:
"echo {1}" "echo {2}" "echo {1}, {2}!" "echo {1} {2} {1} {2}"

output:
- - hello
  - world
  - hello, world!
  - hello world hello world
- - brain
  - wash
  - brain, wash!
  - brain wash brain wash

