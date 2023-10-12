



def auxiliary_go(self, current_gameboard, auxiliary_go_func):
    current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], auxiliary_go_func)