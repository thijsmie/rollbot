import sys
from datetime import timedelta
from rollbot.interpreter.calculator import distribute, EvaluationError
from rollbot.varenv import VarEnv
from lark.exceptions import UnexpectedInput


if __name__ == "__main__":
    varenv_name = sys.stdin.readline().strip()
    expression = sys.stdin.readline().strip()

    try:
        env = VarEnv(varenv_name)
    except:
        print("No such environment")
        sys.exit(1)

    try:
        xbins, data, num_rolls = distribute(expression, timedelta(seconds=5), env)
    except EvaluationError as e:
        print(e.args[0])
        sys.exit(1)
    except UnexpectedInput as e:
        print(f"Unexpected input: ```\n{e.get_context(expression)}```")
        sys.exit(1)
    except:
        print("Server error")
        sys.exit(1)

    print(" ".join(str(x) for x in xbins))
    print(" ".join(str(x) for x in data))
    print(num_rolls)
