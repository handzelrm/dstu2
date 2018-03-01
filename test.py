import re
test = 'Successfully created resource "Patient/15/_history/1" in 18ms'

regex = re.compile(r'[a-z]\/(\d+)\/',re.IGNORECASE)

print(regex.search(test).group(1))
