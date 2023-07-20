import base64
import os

from sympy import diff, integrate, print_latex, latex, pretty, solve, Eq
from sympy.parsing.sympy_parser import *
from sympy.plotting import plot
from io import BytesIO

from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html", HOSTNAME=os.getenv("DETA_SPACE_APP_HOSTNAME"))

@app.route('/api/univariate')
def plotter():
    args = request.args

    try:
        exp = parse_expr(args['func'], transformations=standard_transformations + (split_symbols, implicit_multiplication, function_exponentiation, convert_xor))

        buf = BytesIO()

        p = plot(exp, show=False)
        p._backend = p.backend(p)
        p._backend.process_series()
        p._backend.fig.savefig(buf, format="png")

        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return {
            "variable": pretty(exp.atoms(Symbol).pop()),
            "expression": latex(exp),
            "plot": data,
            "diff": latex(diff(exp)),
            "integral": latex(integrate(exp)),
            "solution": [latex(i) for i in solve(Eq(exp, 0))]
        }
    except Exception as e:
        print(e)
        return f"Bad Request", 400

if __name__ == '__main__':
    app.run()
