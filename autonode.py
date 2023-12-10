
def get_node_names_mappings(classes):
    node_names = {}
    node_classes = {}
    for cls in classes:
        # check if "custom_name" attribute is set
        if hasattr(cls, "custom_name"):
            node_names[cls.__name__] = cls.custom_name
            node_classes[cls.__name__] = cls
    return node_names, node_classes

def node_wrapper(container):
    def wrap_class(cls):
        container.append(cls)
        return cls
    return wrap_class

