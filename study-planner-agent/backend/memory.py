memory = {}

def save(goal, data):
    memory[goal] = data

def get(goal):
    return memory.get(goal, "No memory found")