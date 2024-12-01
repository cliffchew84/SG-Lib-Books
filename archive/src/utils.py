from fastapi.templating import Jinja2Templates

# Jinja2 Templates
templates = Jinja2Templates(directory="templates")


# Helper functions
def pg_links(offset, total):
    """Create pagination for the output of my NLB Search"""
    items = 30
    previous = offset - items if offset != 0 else None
    current = offset
    next = offset + items if (offset + items < total) else None
    last = items * (total // items) if next is not None else None

    return {"previous": previous, "current": current, "next": next, "last": last}
