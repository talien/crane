import concurrent.futures

def parallel_map_reduce(map_func, reduce_func, iterable, output_init):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = map(lambda x: executor.submit(map_func, x), iterable)
    result = reduce(lambda aggregate, item: reduce_func(aggregate, item.result()), concurrent.futures.as_completed(futures), output_init)
    return result
