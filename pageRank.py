from sys import argv, getsizeof
import re
import copy
import time
import operator
import math

def main():
    input_f, input_type = check_args()

    before_read = time.time()

    edge_labels, edge_values = parse_input(input_f, input_type)
    graph = generate_graph(edge_labels, edge_values)     # Set Notation

    after_read = time.time()
    total_read_time = (after_read- before_read) *1000

    #pretty_print(graph)
    
    before_process = time.time()

    page_ranks, num_iterations = page_rank(graph)

    after_process = time.time()

    total_process_time = (after_process - before_process)*1000

    sorted_nodes = sorted(page_ranks.items(), key=operator.itemgetter(1), reverse=True)

    standing = 1

    for v, rank in sorted_nodes:
        print('{} {:>30}  PageRank: {:>15.15f}'.format(standing, v, rank))
        standing += 1
    
    print('---------------------------------------------------------------')
    print('Read time (ms):', total_read_time)
    print('Process time (ms):', total_process_time)
    print('Number of iterations:', num_iterations)
    #print('Graph_mem:', getsizeof(graph))
    #print('Labels_mem:', getsizeof(edge_labels), 'Values_mem:', getsizeof(edge_values))

# All lists declared inside function are indexed by vertices.index(vertex)
def page_rank(graph):
    prev_ranks = {}
    curr_ranks = {}

    vertices = [key for key in graph]
    out_edges = {}
    in_edges = {}

    epsilon = 0.1
    probability = 1- (1/len(vertices))

    num_iterations = 0

    for v in vertices:
        # Initial ranks
        prev_ranks[v] = 1/len(vertices)
        out_edges[v] = []
        in_edges[v] = []
        # Store outbound/inbound edges for every vertex
        for edge in graph[v]:
            if v == edge[0]:
                out_edges[v].append(edge)
            if v == edge[1]:
                in_edges[v].append(edge)

    while(1):
        num_iterations += 1
        # Compute rank for every vertex
        for v in vertices:
            # Probability of reaching random new node
            chose_new_node = (1-probability)*(1/len(vertices))
            # Probability of reaching node from outgoing edge
            follow_link = 0
            # Obtain parent nodes for current v
            for j in in_edges[v]:
                follow_link +=  1/len(out_edges[j[0]]) \
                    * prev_ranks[j[0]]
            follow_link *= probability
            curr_ranks[v] = chose_new_node + follow_link

        # Terminate is page_rank has not updated by a significant amount
        if((sum([math.fabs(curr_ranks[x] - prev_ranks[x]) 
            for x in curr_ranks]) < epsilon)):
            return curr_ranks, num_iterations

        prev_ranks = copy.deepcopy(curr_ranks)

# Prints each vertex, then all of that vertex's in/out edges
def pretty_print(graph):
    for v in graph:
        print(v, graph[v])

'''
Outputs graph data structure in set notation
Determines edge direction based on edge values
All input data is treated as directed graph data
'''
def generate_graph(edge_labels, edge_values):
    graph = {}
    for i, label_pair in enumerate(edge_labels):
        # Add vertices
        from_v = label_pair[0]
        to_v = label_pair[1]
        if from_v not in graph:
            graph[from_v] = set()
        if to_v not in graph:
            graph[to_v] = set()
        
        # Check for 0 valued edges
        if(all(val == 0 for val in edge_values[i])):
            graph[from_v].add(tuple(label_pair))
            graph[to_v].add(tuple(label_pair))

        # Higher edge value = to vertex
        # Lower edge value = from vertex
        else:
            to_v = label_pair[edge_values[i].index((max(edge_values[i])))]
            from_v = label_pair[edge_values[i].index((min(edge_values[i])))]
            edge = tuple([from_v, to_v])
            graph[to_v].add(edge)
            graph[from_v].add(edge)

    return graph

'''
Outputs edge labels and edge values for the given nodes
Assumes input type matches provided file
Node Values of 0 indicate that edge direction is
    from label 0 to label 1
'''
def parse_input(input_f, input_type):
    node_data = open(input_f, 'r')
    edge_labels = []
    edge_values = []

    # Small data set is comma separated
    # has 4 relevant columns
    if(input_type == 'SMALL'):
        num_cols = 4
        # Remove double quotes
        edge_data = [re.sub('[\"]', '', line) \
            .split(',')[:num_cols] for line in node_data]

        # Append node label/value tuples to maintain connection info
        for edge in edge_data:
            edge_labels.append([edge[0].strip(), edge[2].strip()])
            edge_values.append([int(edge[1]), int(edge[3])])

    # SNAP data set is tab separated
    # has 2 relevant columns and misc text in beginning
    elif(input_type == 'SNAP'):
        num_cols = 2
        # Remove double quotes
        edge_data = [re.sub('\"', '', line) \
            .split('\t')[:num_cols] for line in node_data]
        
        # Append node label/value tuples to maintain connection info
        for edge in edge_data:
            # Skip document comments
            if(edge[0][0] == '#'):
                continue
            edge_labels.append([edge[0].strip(), edge[1].strip()])
            # No values are provided with SNAP data set
            edge_values.append([0, 0])

    else:
        print('Usage: dataset_type must be either SNAP or SMALL')
        exit()

    node_data.close()
    return edge_labels, edge_values

# No type/value checking is done
def check_args():
    argc = len(argv)

    if((argc != 2) & (argc != 3)):
        print('Usage: python3 pageRank.py <file_name.csv> '
            + '[dataset_type]')
        exit()
    if(argc == 2):
        return argv[1], 'SMALL'
    else:
        return argv[1], argv[2]

if __name__ == '__main__':
    main()