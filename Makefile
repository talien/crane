clean:
	find . -name "*.pyc" -type f -delete
	rm -f .coverage
	rm -rf htmlcov
check:
	PYTHONPATH="." py.test
coverage:
	PYTHONPATH="." py.test --cov .
coverage-html:
	PYTHONPATH="." py.test --cov . --cov-report=html
lint:
	pylint crane || exit 0
