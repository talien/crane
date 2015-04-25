clean:
	find . -name "*.pyc" -type f -delete
check:
	PYTHONPATH="." py.test
