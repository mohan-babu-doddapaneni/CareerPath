# Importing the hashlib library
import hashlib
def get_hash(data):

	hash_value = hashlib.md5(data.encode()).hexdigest()
	return hash_value

if __name__ == '__main__':
	print(get_hash('sample'))