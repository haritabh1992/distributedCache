class Cache:
    def __init__(self):
        self.keyValueStore = {}

    def reinit(self):
        self.keyValueStore.clear()

    def getValue(self, key):
        return self.keyValueStore.get(key, None)

    def setValue(self, key, value):
        self.keyValueStore[key] = value

    def localFetch(self, key):
        outputJson = {}

        cachedValue = self.getValue(key)
        if cachedValue is None:
            outputJson["status"] = "Not Found"
        else:
            outputJson["status"] = "Success"

        outputJson["key"] = key
        outputJson["value"] = cachedValue

        return outputJson

    def localSet(self, key, value):
        outputJson = {}
        outputJson["status"] = "Succcess"
        outputJson["key"] = key
        outputJson["value"] = value

        self.setValue(key, value)

        return outputJson


# for unit testing - Improve to have a testing framework
def main():
    myCache = Cache()
    print("myCache.getValue(\"abcd\") = ", myCache.getValue("abcd"))
    print("myCache.setValue(\"abcd\", \"pqrs\") = ",
          myCache.setValue("abcd", "pqrs"))
    print("myCache.getValue(\"abcd\") = ", myCache.getValue("abcd"))

    print("cache.reinit()", myCache.reinit())
    print("myCache.getValue(\"abcd\") = ", myCache.getValue("abcd"))


if __name__ == "__main__":
    main()
