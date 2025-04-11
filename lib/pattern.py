import re

# "005214zhangsan_zha-123.zip" --> "005214zhangsan"
NAME_SPLIT_PATTERN = re.compile(r"""^([^_]+)(?:_.*)?$""")

# "005214zhangsan" --> "005214", "zhangsan"
STUDENT_ID_NAME_PATTERN = re.compile(r"""^([0-9]+)([^0-9]+)$""")
