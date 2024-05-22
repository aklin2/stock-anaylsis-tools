from flask import Flask, redirect, render_template, request, url_for
from datetime import datetime, timedelta
from lib import get_adj_close_plot, get_monte_carlo_plot
import base64

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ticker = request.form["ticker"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        iterations = request.form["iterations"]
        trading_days = request.form["trading_days"]

        return redirect(
            url_for(
                "monte_carlo",
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                iterations=iterations,
                trading_days=trading_days,
            )
        )
    today = datetime.today().strftime("%Y-%m-%d")
    last_year = datetime.now() - timedelta(days=365)
    last_year = last_year.strftime("%Y-%m-%d")
    return render_template("index.html", last_year=last_year, today=today)


@app.route("/monte_carlo/")
def monte_carlo():
    # Grab inputs
    ticker = request.args.get("ticker")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    iterations = request.args.get("iterations")
    trading_days = request.args.get("trading_days")

    # Generate plot
    try:
        adj_close_img = get_adj_close_plot(ticker, start_date, end_date)
        adj_close_img_base64 = base64.b64encode(adj_close_img.getvalue()).decode(
            "utf-8"
        )

        monte_carlo_img = get_monte_carlo_plot(
            ticker, start_date, end_date, trading_days, iterations
        )
        monte_carlo_img_base64 = base64.b64encode(monte_carlo_img.getvalue()).decode(
            "utf-8"
        )
    except ValueError:
        return render_template("error.html")

    return render_template(
        "monte_carlo.html",
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        trading_days=trading_days,
        iterations=iterations,
        adj_close_img_data=adj_close_img_base64,
        monte_carlo_img_data=monte_carlo_img_base64,
    )


if __name__ == "__main__":
    app.run(debug=True)
