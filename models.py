import cplex

class BMatchingAndTree(object):
    def __init__(self, nodes,edges_source):
        self.nodes = nodes
        self.edges_source = edges_source
        self.names_variables_b_matching = []
        self.names_variables_tree = []
    
    def create_model(self):
        self.c = cplex.Cplex()
        self.c.set_results_stream(None)
        self.c.set_log_stream(None)
        self.add_variables()
        self.create_constraints()
        self.add_function_objective()

    def add_variables(self):
        self.names_variables_b_matching = []
        self.names_variables_tree = []
        variables_aux = []
        for i in self.edges_source:
            edges = self.edges_source[i]
            variables_aux.append('a%d'%i)
            for edge in edges:
                dest = edge[0]
                self.names_variables_b_matching.append('b%d,%d' %(i,dest))
                self.names_variables_tree.append('t%d,%d' %(i,dest))
        self.c.variables.add(names = self.names_variables_b_matching, types = [self.c.variables.type.binary] * len(self.names_variables_b_matching))
        self.c.variables.add(names = self.names_variables_tree, types = [self.c.variables.type.binary] * len(self.names_variables_tree))
        self.c.variables.add(names = variables_aux, types = [self.c.variables.type.integer] * len(variables_aux),
                             lb=[0]*len(variables_aux),ub=[len(self.nodes)]*len(variables_aux))
        
    def create_constraints(self):        
        edges_start_i_tree = []
        self.c.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = ['a0'], val = [1])],
                                                      senses = ["E"],
                                                      rhs = [0])
        for i in self.edges_source:
            edges_start_i_b_matching = []
            edges = self.edges_source[i]
            for edge in edges:
                dest = edge[0]
                edges_start_i_b_matching.append('b%d,%d' %(i,dest))
                edges_start_i_tree.append('t%d,%d' %(i,dest))
                #self.c.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = ['t%d,%d'%(i,dest),'b%d,%d'%(i,dest)], val = [1, -1])],
                #                                      senses = ["E"],
                #                                      rhs = [0])
                self.c.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = ['a%d'%i,'a%d'%dest,'t%d,%d'%(i,dest)], val = [1, -1,len(self.nodes)])],
                                                      senses = ["L"],
                                                      rhs = [len(self.nodes)-1])
            self.c.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = edges_start_i_b_matching, val = [1] * len(edges_start_i_b_matching))],
                                                     senses = ["L"],
                                                     rhs = [self.nodes[i]])
        self.c.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = edges_start_i_tree, val = [1] * len(edges_start_i_tree))],
                                                  senses = ["E"],
                                                  rhs = [len(self.nodes)-1])

    def add_function_objective(self, multipli_lagrangean={}):
        objective_b_matching = []
        objective_tree = []
        for i in self.edges_source:
            edges = self.edges_source[i]
            for edge in edges:
                dest = edge[0]
                cost = edge[1]
                objective_b_matching.append(('b%d,%d' %(i,dest), cost/2.0 - multipli_lagrangean.get((i,dest),0)))
                objective_tree.append(('t%d,%d' %(i,dest), cost/2.0  + multipli_lagrangean.get((i,dest),0)))
        self.c.objective.set_linear(objective_b_matching+objective_tree)
        self.c.objective.set_sense(self.c.objective.sense.minimize)