class Properties:
    __DEFAULT_KEY_DELIMITER = "="
    __DEFAULT_VALUE_DELIMITER = ","

    def __init__(self, filename, delimiter=__DEFAULT_VALUE_DELIMITER):
        self.filename = filename
        self.__properties = {}
        self.__DEFAULT_VALUE_DELIMITER = delimiter
        self.__init_properties()

    def __init_properties(self):
        with open(self.filename, "r") as file:
            for line in file:
                if line.find(self.__DEFAULT_KEY_DELIMITER) == -1:
                    continue
                key, value = line.strip().split(self.__DEFAULT_KEY_DELIMITER)
                if value.find(self.__DEFAULT_VALUE_DELIMITER) == -1:
                    self.__properties[key] = value
                else:
                    value_list = value.split(self.__DEFAULT_VALUE_DELIMITER)
                    self.__properties[key] = value_list

    def get_property(self, key=None):
        if key is None:
            return self.__properties
        else:
            return self.__properties[key]

    def set_property(self, key, value):
        self.__properties[key] = value

    def update_properties(self):
        with open(self.filename, "w") as file:
            for key in self.__properties.keys():
                key_value_str = self.__generate_prop_str(key)
                file.write("%s" % key_value_str)

    def __generate_prop_str(self, key):
        key_value_str = "%s%c" % (key, self.__DEFAULT_KEY_DELIMITER)
        if isinstance(self.__properties[key], list):
            prop_list = self.__properties[key]
            prop_list_len = len(prop_list)
            for i in range(prop_list_len - 1):
                key_value_str += "%s," % prop_list[i]
            key_value_str += "%s\n" % prop_list[prop_list_len - 1]
        else:
            key_value_str += "%s\n" % self.__properties[key]
        return key_value_str
