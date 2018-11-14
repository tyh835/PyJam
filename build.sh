# clean-up step
rm -rf build dist pyjam.egg-info
pip3 uninstall pyjam -y

# build
pipenv run python setup.py bdist_wheel

# install
pip3 install dist/*.whl

# upload
aws s3 sync dist s3://tyh835-bin