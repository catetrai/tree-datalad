def pytest_make_parametrize_id(config, val, argname):
    if isinstance(val, list):
        return f"{argname}={val}"
    # return None to let pytest handle the formatting
    return None
