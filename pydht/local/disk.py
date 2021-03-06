import math
import os
import os.path
import shutil


# LocalDiskDHT implements a DHT stored on disk in a single machine. The DHT
# contains a list of hash values and their occurrences in the format:
# <hashValue:occurrences>.
class LocalDiskDHT:
    # hashSize is in bits, numOfHt is the number of hath tables to use in the
    # distributed hash table, and path is the directory location where the DHT
    # is stored on disk.
    def __init__(self, hashSize, numOfHT, path):
        self.__hashSize = hashSize
        self.__numOfHT = numOfHT

        # Calculate the hash table size.
        size = math.pow(2, hashSize) / numOfHT
        self.__htSize = int(size)
        if int(size) != size:
            self.__numOfHT = self.__numOfHT + 1
            print "Adjusting number of hash tables in '" + path + "' to " + \
                str(self.__numOfHT)

        self.__path = path
        self.__createDirectory()


    # Create the hash table directory, first remove it if it exists.
    def __createDirectory(self):
        if os.path.isdir(self.__path):
            shutil.rmtree(self.__path, ignore_errors=True)
        os.makedirs(self.__path)
        

    # insert adds a new hashValue into the DHT. hashValue is an integer or a long
    # integer.
    def insert(self, hashValue):
        # Calculate the HT ID of this hashValue.
        htId = self._calculateHTId(hashValue)

        # Read the counter of the hash value.
        counter = self.read(hashValue)

        # If the hash value was found (i.e., counter > 0), copy the whole file
        # without this hash value.
        if counter > 0:
            self.__copyHT(htId, hashValue)

        # Append the hash with its correct counter. If the hash value is new,
        # counter at this point is 0, otherwise it will have a greater value. In
        # both cases, add 1 to the counter.
        self.__append(htId, hashValue, counter + 1)


    # read reads the number of occurrences of a given hashValue.
    def read(self, hashValue):
        # Calculate the HT ID of this hash value.
        htId = self._calculateHTId(hashValue)

        counter = 0
        fileName = os.path.join(self.__path, str(htId))
        # Open the corresponding on disk file and look for the matching
        # hashValue.
        if os.path.isfile(fileName):
            with open(fileName, "r") as htFile:
                for line in htFile:
                    lineChunks = line.split(":")
                    if lineChunks[0] == str(hashValue):
                        counter = int(lineChunks[1])
                        break

        return counter


    # exists checks whether a specific hashValue exists in the DHT.
    def exists(self, hashValue):
        counter = self.read(hashValue)
        if counter > 0:
            return True

        return False


    # _calculateHTId calculates the HT ID of a given hashValue.
    def _calculateHTId(self, hashValue):
        htId = int(hashValue / self.__htSize)
        # This throws and error if htId is larger than number of hash tables.
        assert htId <= self.__numOfHT
        return htId


    # _append appends hashValue to the end of htId hash table.
    def __append(self, htId, hashValue, counter):
        fileName = os.path.join(self.__path, str(htId))
        with open(fileName, "a+") as htFile:
            htFile.write(str(hashValue) + ":" + str(counter) + "\n")


    # __copyHT copies the specified htID hash table without a given hashValue.
    def __copyHT(self, htId, hashValue):
        # Steps:
        #   1. Rename the current htId file with '.tmp' extension.
        #   2. Create an empty file for htId.
        #   3. Copy all hash values from the '.tmp' file to the empty file,
        #      without the given hashValue.
        #   4. Remove the '.tmp' file.
        fileName = os.path.join(self.__path, str(htId))
        tmpFileName = os.path.join(self.__path, str(htId) + ".tmp")
        os.rename(fileName, tmpFileName)
        with open(tmpFileName, "r") as inFile:
            with open(fileName, "w+") as outFile:
                for line in inFile:
                    # Read line and ignore the same hashValue.
                    lineChunks = line.split(":")
                    if lineChunks[0] == str(hashValue):
                        continue

                    # Write line.
                    outFile.write(line)
        # Remove the tmp file.
        os.remove(tmpFileName)


    # calculateCollision calculates the collision probability of this hash table.
    def calculateCollision(self):
        # Total contains the sum of all hash value occurrences in the DHT.
        total = 0
        # Count contains the sum of occurrences of hash values with collision,
        # e.g., occurrence value larger than 1.
        count = 0
        for filePath in [os.path.join(self.__path, f) for f in
                         os.listdir(self.__path) if
                         os.path.isfile(os.path.join(self.__path, f))]:
            with open(filePath, "r") as inFile:
                for line in inFile:
                    chunk = line.split(":")
                    if int(chunk[1]) > 1:
                        count = count + int(chunk[1])
                    total = total + int(chunk[1])

        return count / float(total)


    # countCollision counts the hash buckets that have collision, the number of
    # inserted hash values that collide, and the total number of hash values
    # inserted into the DHT.
    def countCollision(self):
        # hashCount contains the number of hash table buckets that have
        # collision.
        hashCount = 0
        # valueCount contains the sum of occurrences of hash values with
        # collision, e.g., occurrence value larger than 1.
        valueCount = 0
        # totalCount contains the sum of all hash value occurrences in the DHT.
        totalCount = 0
        for filePath in [os.path.join(self.__path, f) for f in
                         os.listdir(self.__path) if
                         os.path.isfile(os.path.join(self.__path, f))]:
            with open(filePath, "r") as inFile:
                for line in inFile:
                    chunk = line.split(":")
                    if int(chunk[1]) > 1:
                        hashCount = hashCount + 1
                        valueCount = valueCount + int(chunk[1])
                    totalCount = totalCount + int(chunk[1])

        return (hashCount, valueCount, totalCount)
