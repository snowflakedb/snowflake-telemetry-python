# Run setup.py in isolated mode (-I) so the build does not pick up stray
# modules from the working directory. -I is available on all supported
# Pythons (>=3.4), unlike -P/PYTHONSAFEPATH which require Python >=3.11.
${PYTHON} -I setup.py install --single-version-externally-managed --record=record.txt
