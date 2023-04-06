from pyformlang.cfg import CFG


def cfg_to_whnf(cfg: CFG) -> CFG:
    """
    Returns CFG in Weak Normal Chomsky Form that is equivalent to the original
    :param cfg: CFG
    :return: CFG in Weak Normal Chomsky Form
    """
    cfg1 = cfg.eliminate_unit_productions().remove_useless_symbols()
    long_term = cfg1._get_productions_with_only_single_terminals()
    new_rules = set(cfg1._decompose_productions(long_term))
    return CFG(start_symbol=cfg1.start_symbol, productions=new_rules)


def cfg_from_file(path: str) -> CFG:
    """
    Returns CFG built from the text file
    :param path: path to the file with CFG description
    :return: CFG built by description in file
    """
    with open(path) as file:
        return CFG.from_text(file.read())


def whnf_from_file(path: str) -> CFG:
    return cfg_to_whnf(cfg_from_file(path))
