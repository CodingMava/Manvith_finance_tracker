# Redundant template loader removed to ensure filesystem priority
TEMPLATES_DATA = {}
class DictTemplateLoader:
    def __init__(self, *args, **kwargs): pass
    def get_template_sources(self, *args, **kwargs): return []
    def get_contents(self, *args, **kwargs): raise Exception("Disabled")
