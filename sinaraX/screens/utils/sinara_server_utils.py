import os
from multiprocessing import cpu_count


def get_cpu_cores_limit():
    cpu_cores = cpu_count()
    cores_reserve_for_host = 1
    if not cpu_cores or cpu_cores <= cores_reserve_for_host:
        result = 1
    else:
        result = cpu_cores - cores_reserve_for_host
    return result


def get_system_memory_size():
    return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")


def get_memory_size_limit():
    total_mem_bytes = get_system_memory_size()
    bytes_reserve_for_host = int(2 * 1024.0**3)  # Reserve 2 Gb by default
    if total_mem_bytes <= bytes_reserve_for_host:
        result = int(total_mem_bytes * 0.7)
    else:
        result = int(total_mem_bytes - bytes_reserve_for_host)
    return result


def get_default_shm_size():
    total_mem_bytes = get_system_memory_size()
    return int(total_mem_bytes / 6)
