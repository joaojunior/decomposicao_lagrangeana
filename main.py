import sys

from models import BMatchingAndTree
import colect_time

def read_instance(file_name):
    f = open(file_name, 'r')
    line = f.readline()
    line = line.split()
    numbers_nodes = int(line[0])
    numbers_edges = int(line[1])
    edges_source = {}
    nodes = {}
    for i in xrange(numbers_nodes):
        edges_source[i] = []
    for i in xrange(numbers_edges):
        line = f.readline()
        line = line.split()
        source = int(line[0]) - 1
        dest = int(line[1]) - 1
        cost = int(line[2])
        edges_source[source].append((dest,cost))
    for i in xrange(numbers_nodes):
        line = f.readline()
        line = line.split()
        node = int(line[0]) - 1
        b = int(line[1])
        nodes[node] = b
    f.close()
    return nodes,edges_source

def create_pi(bMatchingAndTree):
    pi = {}
    for i in bMatchingAndTree.edges_source:
        edges = bMatchingAndTree.edges_source[i]
        for edge in edges:
            dest = edge[0]
            pi[(i,dest)] = 0
    return pi

def update_pi(best_pi, bMatchingAndTree, UB, solution_value, u=0.01):
    norm_v = 0
    solution = bMatchingAndTree.c.solution
    for i in bMatchingAndTree.edges_source:
        edges = bMatchingAndTree.edges_source[i]
        for edge in edges:
            dest = edge[0]
            norm_v += (solution.get_values('t%d,%d' %(i,dest)) - solution.get_values('b%d,%d' %(i,dest))) ** 2
    if norm_v == 0:
        norm_v = 1
    s = u * (float(UB - solution_value)/norm_v)
    pi = {}
    for edge in best_pi:
        source = edge[0]
        dest = edge[1]
        pi[(edge)] = best_pi[(edge)] + s * (solution.get_values('t%d,%d' %(source,dest)) - solution.get_values('b%d,%d' %(source,dest))) ** 2
    return pi
        

def volume(file_name,UB):
    MAX_ITER = 500000
    MAX_TIME_SEC = 7200
    nodes,edges_source = read_instance(file_name)
    start = colect_time.cpu_time()
    bMatchingAndTree = BMatchingAndTree(nodes,edges_source)
    bMatchingAndTree.create_model()
    t = 0
    pi_t = create_pi(bMatchingAndTree)
    best_pi = create_pi(bMatchingAndTree)
    best_lower_bound = 0
    while UB - best_lower_bound > 1 and t < MAX_ITER and colect_time.cpu_time() - start < MAX_TIME_SEC:
        bMatchingAndTree.add_function_objective(pi_t)
        bMatchingAndTree.c.solve()
        solution_value = bMatchingAndTree.c.solution.get_objective_value()
        pi_t = update_pi(best_pi, bMatchingAndTree, UB, solution_value, u=0.01)
        if solution_value > best_lower_bound:
            best_lower_bound = solution_value
            best_pi = pi_t
        else:
            break
        t += 1
    print file_name, best_lower_bound, t, colect_time.cpu_time()

def main(file_name, UB):
    #nodes,edges_source = read_instance(file_name)
    #start = colect_time.cpu_time()
    #bMatchingAndTree = BMatchingAndTree(nodes,edges_source)
    #bMatchingAndTree.create_model()
    #bMatchingAndTree.c.solve()
    #solution = bMatchingAndTree.c.solution
    #print file_name, solution.get_objective_value(),colect_time.cpu_time()
    volume(file_name, UB)
        
if __name__ == '__main__':
    if len(sys.argv) == 3:
        name_file = sys.argv[1]
        UB = int(sys.argv[2])
        main(name_file, UB)
