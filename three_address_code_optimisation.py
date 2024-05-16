class Optimisation:
    def __init__(self, three_address_code: dict, function_call_tracking: dict):
        self.three_address_code = three_address_code
        self.function_call_tracking = function_call_tracking

    def __optimisation(self):
        for function in self.function_call_tracking:
            if not self.function_call_tracking[function]:
                del self.three_address_code[function]

    def start(self):
        self.__optimisation()
        print(self.three_address_code)
