def deduplicate_list(duplicated_list):
    deduplicated_list = list()

    for item in duplicated_list:
        if item not in deduplicated_list:
            deduplicated_list.append(item)

    return deduplicated_list