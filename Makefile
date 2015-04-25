clean:
	find . -name "*.pyc" -type f -delete
	rm crane/.coverage
	rm crane/htmlcov
check:
	PYTHONPATH="." py.test
coverage:
	PYTHONPATH="." py.test --cov .
coverage-html:
	PYTHONPATH="." py.test --cov . --cov-report=html
