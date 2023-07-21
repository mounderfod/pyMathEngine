import base64
import os

import flask
from sympy import diff, integrate, print_latex, latex, pretty, solve, Eq, nsolve, limit, oo, solveset
from sympy.parsing.sympy_parser import *
from sympy.plotting import plot
from io import BytesIO

from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html", HOSTNAME=os.getenv("DETA_SPACE_APP_HOSTNAME"))

@app.route('/api/equation')
def equation():
    args = request.args

    try:
        lhs = parse_expr(args['lhs'], transformations=standard_transformations + (split_symbols, implicit_multiplication, function_exponentiation, convert_xor))
        rhs = parse_expr(args['rhs'], transformations=standard_transformations + (split_symbols, implicit_multiplication, function_exponentiation, convert_xor))

        response = {'solution': []}

        eq = Eq(lhs, rhs)
        try:
            for i in eq.atoms(Symbol):
                response['solution'].append(latex(i) + "=" + latex(solveset(eq, i)))
        except NotImplementedError:
            response['solution'] = "\\text{Solution could not be calculated.}"

        response = flask.jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        print(e)
        return f"Bad Request", 400

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

        try:
            solution = [latex(i) for i in solveset(Eq(exp, 0))]
        except NotImplementedError:
            solution = "\\text{Solution could not be calculated.}"

        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        response = flask.jsonify({
            "variable": pretty(exp.atoms(Symbol).pop()),
            "expression": latex(exp),
            "plot": data,
            "diff": latex(diff(exp)),
            "integral": latex(integrate(exp)),
            "limit_inf": latex(limit(exp, pretty(exp.atoms(Symbol).pop()), oo)),
            "limit_zero": latex(limit(exp, pretty(exp.atoms(Symbol).pop()), 0)),
            "solution": solution
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        print(e)
        return f"Bad Request", 400

if __name__ == '__main__':
    app.run()
