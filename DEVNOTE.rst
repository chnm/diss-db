Development Notes
=================

Database Fixture Encoding Issues
---------------------------------

When loading fixtures with ``python manage.py loaddata db.json``, you may encounter Unicode encoding errors if the fixture contains accented characters (e.g., Spanish names with é, ñ, etc.).

1. Detect the current encoding::

    python3 -c "
    import chardet
    with open('db.json', 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        print(f'Detected encoding: {result}')
    "

2. Convert to UTF-8::

    python3 -c "
    with open('db.json', 'r', encoding='windows-1252') as f:
        content = f.read()
    with open('db.json', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Converted db.json from Windows-1252 to UTF-8')
    "

App Name Migration
------------------

If migrating from an old project where the Django app was named "dissertations", update model references in fixtures::

    sed -i.bak 's/"dissertations\./"dissdb\./g' db.json

This replaces all instances of "dissertations." with "dissdb." in the fixture file.
