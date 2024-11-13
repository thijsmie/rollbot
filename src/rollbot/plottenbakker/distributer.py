import logging
import sys
from datetime import timedelta

import structlog
from lark.exceptions import UnexpectedInput

from rollbot.interpreter.calculator import EvaluationError, distribute
from rollbot.varenv import VarEnv

if __name__ == "__main__":
    # Disable all logging in distributer process
    logging.disable(logging.CRITICAL)
    structlog.configure(logger_factory=lambda: logging.getLogger())

    varenv_name = sys.stdin.readline().strip()
    expression = sys.stdin.readline().strip()

    try:
        env = VarEnv(varenv_name, "", "")
    except Exception as e:
        print(f"No such environment {e}")
        sys.exit(1)

    try:
        data = distribute(expression, timedelta(seconds=5), env)
        if not data:
            print("Unprocessable input")
            sys.exit(1)
        xbins, data, num_rolls = data
    except EvaluationError as e:
        print(e.args[0])
        sys.exit(1)
    except UnexpectedInput as e:
        print(f"Unexpected input: ```\n{e.get_context(expression)}```")
        sys.exit(1)
    except Exception:
        print("Server error")
        sys.exit(1)

    print(" ".join(str(x) for x in xbins))
    print(" ".join(str(x) for x in data))
    print(num_rolls)
