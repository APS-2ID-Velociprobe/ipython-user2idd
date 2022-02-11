""" Trajectory Tools """

__all__ = """
	create_dirr
	""".split()

import os

def create_dir(dirname):
	if not os.path.exists(dirname):  #create directory
		os.makedirs(dirname, mode=0o0777)
		os.chmod(dirname,0o0777)
		print("Creating directory:"+dirname)
	else:
		print("The directory already exists!")

