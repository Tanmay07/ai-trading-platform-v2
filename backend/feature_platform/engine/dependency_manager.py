class DependencyManager:
    """
    Resolves the execution order of feature categories to prevent circular dependencies
    and guarantee prerequisites are computed first.
    """
    def __init__(self):
        self.graph = {}
        self.in_degree = {}
        
    def add_category(self, category_name: str, depends_on: list = None):
        if depends_on is None:
            depends_on = []
            
        if category_name not in self.graph:
            self.graph[category_name] = []
            self.in_degree[category_name] = 0
            
        for dep in depends_on:
            if dep not in self.graph:
                self.graph[dep] = []
                self.in_degree[dep] = 0
            self.graph[dep].append(category_name)
            self.in_degree[category_name] += 1
            
    def resolve_execution_order(self) -> list:
        """Topological sort using Kahn's algorithm."""
        queue = [node for node in self.in_degree if self.in_degree[node] == 0]
        order = []
        
        while queue:
            current = queue.pop(0)
            order.append(current)
            
            for neighbor in self.graph.get(current, []):
                self.in_degree[neighbor] -= 1
                if self.in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        if len(order) != len(self.in_degree):
            raise ValueError("Circular dependency detected in feature execution graph!")
            
        return order
