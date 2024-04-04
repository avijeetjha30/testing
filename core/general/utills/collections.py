def deep_update(base_dict, update_with):
    # iterate over each items in the new dict
    for key, value in update_with.items():
        # check if the value is dict
        if isinstance(value, dict):
            base_dict_value = base_dict.get('key')

            # check if the new value is also a dict then run through the same function
            if isinstance(base_dict_value, dict):
                deep_update(base_dict_value, value)
            # if not then set the new value
            else:
                base_dict[key] = value
        # if not a dict then set the new value
        else:
            base_dict[key] = value
    return base_dict
