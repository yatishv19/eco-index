from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "eco_index.db"

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_scores(row):
    # Prototype methodology — weights are intentionally transparent and editable.
    # Lower emissions/intensity and larger reductions receive higher scores.
    intensity = (row["total_emissions"] / 1_000_000) / max(row["revenue_billion"], 0.01)
    carbon = max(0, min(40, 40 * (1 / (1 + intensity / 2))))
    reduction = max(0, min(20, 10 + row["emission_change_pct"] * -0.8))
    renewable = min(15, row["renewable_energy_pct"] * 0.15)
    waste = min(10, row["waste_recycled_pct"] * 0.10)
    water = max(0, min(5, row["water_efficiency_score"]))
    transparency = max(0, min(10, row["transparency_score"]))
    total = round(carbon + reduction + renewable + waste + water + transparency)
    return {
        "carbon": round(carbon, 1),
        "reduction": round(reduction, 1),
        "renewable": round(renewable, 1),
        "waste": round(waste, 1),
        "water": round(water, 1),
        "transparency": round(transparency, 1),
        "total": max(0, min(100, total))
    }

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        industry TEXT NOT NULL,
        country TEXT NOT NULL,
        description TEXT,
        website TEXT,
        reporting_year INTEGER NOT NULL,
        scope1 REAL NOT NULL,
        scope2 REAL NOT NULL,
        scope3 REAL NOT NULL,
        total_emissions REAL NOT NULL,
        revenue_billion REAL NOT NULL,
        renewable_energy_pct REAL NOT NULL,
        waste_recycled_pct REAL NOT NULL,
        water_efficiency_score REAL NOT NULL,
        transparency_score REAL NOT NULL,
        emission_change_pct REAL NOT NULL,
        source_name TEXT NOT NULL,
        source_url TEXT
    );
    """)
    count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    if count == 0:
        demo = [
            ("Apple","Technology","USA","Consumer technology company with published environmental reporting.","https://www.apple.com/environment/","2025",40_000,350_000,12_010_000,12_400_000,416.0,72,86,4.0,9.5,-14,"Apple Environmental Progress Report","https://www.apple.com/environment/"),
            ("Microsoft","Technology","USA","Software, cloud and technology company with environmental reporting.","https://www.microsoft.com/sustainability/","2025",160_000,280_000,13_900_000,14_340_000,245.1,90,85,4.1,9.7,-6,"Microsoft Environmental Sustainability Report","https://www.microsoft.com/en-us/corporate-responsibility/sustainability"),
            ("Google","Technology","USA","Technology company reporting emissions, energy and climate initiatives.","https://sustainability.google/","2025",120_000,210_000,10_900_000,11_230_000,350.0,78,82,4.0,9.6,-13,"Google Environmental Report","https://sustainability.google/"),
            ("Nike","Apparel","USA","Sportswear company with sustainability and supply-chain disclosures.","https://purpose.nike.com/","2025",95_000,210_000,1_500_000,1_805_000,51.4,55,76,3.5,8.6,-8,"Nike Sustainability Report","https://purpose.nike.com/"),
            ("Adidas","Apparel","Germany","Sportswear company reporting climate and circularity metrics.","https://www.adidas-group.com/","2025",70_000,160_000,1_370_000,1_600_000,24.8,61,79,3.6,8.8,-11,"adidas Sustainability Report","https://www.adidas-group.com/en/sustainability/"),
            ("H&M","Apparel","Sweden","Fashion retailer reporting climate, materials and circularity indicators.","https://hmgroup.com/sustainability/","2025",80_000,190_000,1_080_000,1_350_000,22.0,68,72,3.8,8.7,-16,"H&M Group Sustainability Report","https://hmgroup.com/sustainability/"),
            ("Tesla","Automotive","USA","Electric vehicle and energy company with impact reporting.","https://www.tesla.com/impact","2025",110_000,190_000,5_600_000,5_900_000,97.7,45,75,3.2,8.1,-7,"Tesla Impact Report","https://www.tesla.com/impact"),
            ("Toyota","Automotive","Japan","Automotive manufacturer reporting emissions and lifecycle impacts.","https://global.toyota/en/sustainability/","2025",2_100_000,4_200_000,560_000_000,566_300_000,310.0,42,84,3.8,9.1,-9,"Toyota Sustainability Data Book","https://global.toyota/en/sustainability/"),
            ("Volkswagen","Automotive","Germany","Automotive group publishing climate and environmental disclosures.","https://www.volkswagen-group.com/","2025",1_900_000,3_500_000,420_000_000,425_400_000,340.0,38,80,3.6,8.9,-12,"Volkswagen Sustainability Report","https://www.volkswagen-group.com/en/sustainability"),
            ("Coca-Cola","Food & Beverage","USA","Beverage company reporting emissions, packaging, water and waste metrics.","https://www.coca-colacompany.com/sustainability","2025",600_000,900_000,8_500_000,10_000_000,47.1,35,62,3.0,8.4,-5,"Coca-Cola Business & Sustainability Report","https://www.coca-colacompany.com/sustainability"),
            ("PepsiCo","Food & Beverage","USA","Food and beverage company reporting climate and value-chain metrics.","https://www.pepsico.com/sustainability","2025",700_000,1_000_000,11_000_000,12_700_000,91.9,38,68,3.2,8.6,-7,"PepsiCo ESG Summary","https://www.pepsico.com/sustainability"),
            ("Nestlé","Food & Beverage","Switzerland","Food and beverage company reporting climate, agriculture and packaging metrics.","https://www.nestle.com/sustainability","2025",1_200_000,1_600_000,85_000_000,87_800_000,103.0,41,70,3.4,9.0,-10,"Nestlé Creating Shared Value & Sustainability Report","https://www.nestle.com/sustainability"),
            ("Tata Motors","Automotive","India","Indian automotive company reporting climate and energy performance.","https://www.tatamotors.com/","2025",410_000,780_000,6_900_000,8_090_000,55.0,31,73,3.1,8.4,-15,"Tata Motors Sustainability Report","https://www.tatamotors.com/"),
            ("Reliance Industries","Conglomerate","India","Indian conglomerate reporting energy, emissions and environmental indicators.","https://www.ril.com/","2025",8_500_000,5_600_000,20_000_000,34_100_000,125.0,28,65,2.8,8.2,-6,"Reliance Industries Annual Report","https://www.ril.com/"),
            ("Infosys","IT Services","India","IT services company reporting energy, emissions and renewable-energy performance.","https://www.infosys.com/sustainability/","2025",30_000,170_000,210_000,410_000,19.0,78,92,4.4,9.6,-19,"Infosys ESG Report","https://www.infosys.com/sustainability/")
        ]
        conn.executemany("""
        INSERT INTO companies
        (name,industry,country,description,website,reporting_year,scope1,scope2,scope3,total_emissions,
         revenue_billion,renewable_energy_pct,waste_recycled_pct,water_efficiency_score,transparency_score,
         emission_change_pct,source_name,source_url)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, demo)
        conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/company/<int:company_id>")
def company(company_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM companies WHERE id=?", (company_id,)).fetchone()
    all_years = conn.execute("SELECT * FROM companies WHERE id=?", (company_id,)).fetchone()
    conn.close()
    if not row:
        return render_template("404.html"), 404
    data = dict(row)
    data["score"] = calculate_scores(row)
    # Demo trend: derived illustrative prior-year values from current reported total.
    total = row["total_emissions"]
    change = row["emission_change_pct"]
    data["trend"] = [
        {"year": row["reporting_year"]-3, "value": round(total / ((1 + change/100) ** 3), 2)},
        {"year": row["reporting_year"]-2, "value": round(total / ((1 + change/100) ** 2), 2)},
        {"year": row["reporting_year"]-1, "value": round(total / (1 + change/100), 2)},
        {"year": row["reporting_year"], "value": round(total, 2)}
    ]
    return render_template("company.html", company=data)

@app.route("/compare")
def compare():
    conn = get_db()
    rows = conn.execute("SELECT * FROM companies ORDER BY name").fetchall()
    conn.close()
    companies = []
    for r in rows:
        d = dict(r)
        d["score"] = calculate_scores(r)
        companies.append(d)
    return render_template("compare.html", companies=companies)

@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    conn = get_db()
    rows = conn.execute("""
        SELECT id,name,industry,country FROM companies
        WHERE name LIKE ? OR industry LIKE ?
        ORDER BY name LIMIT 10
    """, (f"%{q}%", f"%{q}%")).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/companies")
def api_companies():
    conn = get_db()
    rows = conn.execute("SELECT id,name,industry,country,total_emissions,renewable_energy_pct,emission_change_pct FROM companies ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/company/<int:company_id>")
def api_company(company_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM companies WHERE id=?", (company_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error":"Company not found"}), 404
    data = dict(row)
    data["score"] = calculate_scores(row)
    return jsonify(data)

init_db()

if __name__ == "__main__":
    app.run(debug=True)
