# so in our simulated game the employees interact with each other 
# on each step an employee interacts with every other employee. 
# they interact via Relationship events
# Relationship events look at a an employee stats and the relationship 
# stats of the employee network and then give a pdf for an update that we then sample from with a random var 
# these samples return employee deltas and relationship deltas and we store these delta with the employee. 
# for efficiency we pack the Null deltas with their count number. 
