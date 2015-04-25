clean:
	find . -name "*.pyc" -type f -delete
	rm crane/.coverage
check:
	PYTHONPATH="." py.test
coverage:
	PYTHONPATH="." py.test --cov .
