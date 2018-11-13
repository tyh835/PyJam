# clean-up step
rm -rf build dist pydeploy.egg-info
pip3 uninstall pydeploy -y

# build
pipenv run python setup.py bdist_wheel

# install
pip3 install dist/*.whl
