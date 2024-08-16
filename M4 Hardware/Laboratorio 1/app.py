from flask import Flask, jsonify, request
from flask_restful import Resource, Api, abort
import requests

app = Flask("Drug_OD_API")
api = Api(app)

def load_data():
    url = 'https://data.cdc.gov/api/views/95ax-ymtc/rows.json?accessType=DOWNLOAD'
    response = requests.get(url)
    data = response.json()
    return data['data']

data = load_data()

class Index(Resource):
    def get(self):
        return "Hello World!", 200

class DataByYear(Resource):
    def get(self):
        year = request.args.get('year')
        
        if not year:
            abort(400, message="Year parameter is required.")
        
        filtered_data = [row for row in data if row[17] == year]

        if not filtered_data:
            abort(404, message=f"No data found for year {year}")

        return jsonify(filtered_data)

class AverageDeathsByYear(Resource):
    def get(self):
        year = request.args.get('year')
        
        if not year:
            abort(400, message="Year parameter is required.")
        
        filtered_data = [row for row in data if row[17] == year]
        
        if not filtered_data:
            abort(404, message=f"No data found for year {year}")

        total_deaths = 0
        count = 0
        
        for row in filtered_data:
            try:
                death_rate = float(row[21])
                total_deaths += death_rate
                count += 1
            except (ValueError, TypeError):
                continue

        if count == 0:
            abort(404, message=f"No valid data found for year {year}")

        average_deaths = total_deaths / count

        return jsonify({
            "year": year,
            "average_deaths_per_100000": average_deaths
        })
    
class CompareMaleRace(Resource):
    def get(self):
        year = request.args.get('year')
        
        if not year:
            abort(400, message="Year parameter is required.")

        white_men_data = [row for row in data if row[17] == year and row[15] == "Male: White"]
        black_men_data = [row for row in data if row[17] == year and row[15] == "Male: Black or African American"]
        asian_men_data = [row for row in data if row[17] == year and row[15] == "Male: Not Hispanic or Latino: Asian or Pacific Islander"]

        
        def get_average_deaths(data):
            total_deaths = 0
            count = 0
            for row in data:
                try:
                    death_rate = float(row[21])
                    total_deaths += death_rate
                    count += 1
                except (ValueError, TypeError):
                    continue
            return total_deaths / count if count > 0 else None
        
        avg_white_men = get_average_deaths(white_men_data)
        avg_black_men = get_average_deaths(black_men_data)
        avg_asian_men = get_average_deaths(asian_men_data)

        if avg_white_men is None and avg_black_men is None:
            abort(404, message=f"No valid data found for year {year}")

        return jsonify({
            "base_count": 100000,
            "year": year,
            "average_deaths_white_men": avg_white_men,
            "average_deaths_black_men": avg_black_men,
            "average_deaths_asian_men": avg_asian_men
        })

api.add_resource(Index, "/")
api.add_resource(DataByYear, "/data/year")
api.add_resource(AverageDeathsByYear, "/data/year/average")
api.add_resource(CompareMaleRace, "/data/year/male-race")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
