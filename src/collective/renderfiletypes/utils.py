# -*- coding: utf-8 -*-


SIZE_CONST = {"KB": 1024, "MB": 1024 * 1024, "GB": 1024 * 1024 * 1024}
SIZE_ORDER = ("GB", "MB", "KB")


def human_readable_size(size):
    """ Get a human readable size string. """
    smaller = SIZE_ORDER[-1]

    # if the size is a float, then make it an int
    # happens for large files
    try:
        size = int(size)
    except (ValueError, TypeError):
        return size

    if not size:
        return "0 %s" % smaller

    if isinstance(size, int):
        if size < SIZE_CONST[smaller]:
            return "1 %s" % smaller
        for c in SIZE_ORDER:
            if size // SIZE_CONST[c] > 0:
                break
        return "%.1f %s" % (float(size / float(SIZE_CONST[c])), c)
    return size
