EXIT_STATE=0

python -m unittest tests.test_integration || EXIT_STATE=$?

pylint easy_dash setup.py --rcfile=$PYLINTRC || EXIT_STATE=$?
pylint tests -d all -e C0410,C0411,C0412,C0413,W0109 || EXIT_STATE=$?
flake8 easy_dash setup.py || EXIT_STATE=$?
flake8 --ignore=E123,E126,E501,E722,E731,F401,F841,W503,W504 tests || EXIT_STATE=$?
pyversion="$(python -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')"

if [ "$pyversion" -ge "37" ]; then
    black easy_dash --check || EXIT_STATE=$?
fi

if [ $EXIT_STATE -ne 0 ]; then
    echo "One or more tests failed"
else
    echo "All tests passed!"
fi

exit $EXIT_STATE
