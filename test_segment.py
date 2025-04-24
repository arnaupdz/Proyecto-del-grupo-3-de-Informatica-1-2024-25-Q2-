from node import Node
from segment import Segment

node_a = Node("A", 0.0, 0.0)
node_b = Node("B", 3.0, 4.0)
node_c = Node("C", 6.0, 8.0)

segment_1 = Segment("Segmento 1", node_a, node_b)
segment_2 = Segment("Segmento 2", node_b, node_c)

print(segment_1)
print(segment_2)
