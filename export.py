import pandas as pd

# Daten für das Mittagessen
data_mittagessen = {
    "Menge (g)": [0, 0, 0, 0, 280, 355, 80, 415, 110, 500, 110, 110, 115, 425, 115, 180, 170, 135, 185, 170, 150, 175, 155, 180, 235, 110, 155, 240, 220, 200, 295, 180, 180, 45, 125, 30, 30],
    "Name": [
        "Beeren, roh", "Banane, roh", "Früchte, roh", "Zitrusfrüchte, roh", 
        "Gemüse, roh", "Tomate, roh", "Mais, roh", "Blattsalat roh", 
        "Reis, trocken", "Kartoffel, geschält, roh", "Teigwaren, trocken", 
        "Maisgriess, trocken", "Linsen, getrocknet", "Rote Bohnen gekocht (Kidney)", 
        "Knäckebrot, Vollkorn", "Weizenvollkornbrot", "Poulet, roh", "Rindfleisch mager, roh",
        "Kalb, mager, roh", "Lamm, mager, roh", "Schwein, mager, roh", "Pferd, roh", 
        "Wild, roh", "Lachs, roh", "Dorsch, roh", "Lachs, geräuchert", "Thon im Wasser, abgetr.",
        "Meeresfrüchte", "Tofu", "Quorn", "Skyr nature", "Hüttenkäse, nature", 
        "Hart- und Halbhartkäse, vollfett", "Hühnerei, ganz, roh", "Olivenöl", "Avocado, roh",
        "Nussmischung"
    ],
    "kcal": [0, 0, 0, 0, 75, 75, 75, 75, 380, 380, 380, 380, 380, 380, 380, 380, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 30, 30, 30],
    "pr": [0, 0, 0, 0, 3.6, 2.9, 2.7, 6.5, 7.5, 10.0, 13.5, 9.6, 30.7, 25.6, 12.1, 15.3, 41.4, 28.7, 40.4, 33.5, 33.0, 37.4, 19.5, 42.9, 25.0, 39.4, 37.2, 18, 28, 32.5, 22.6, 12.2, 15.1, 0, 0.4, 0.9],
    "kh": [0, 0, 0, 0, 10.3, 11.4, 12.8, 1.5, 85.1, 78.0, 75.9, 54.6, 55.5, 72.5, 68.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.8, 0.0, 8.8, 8.8, 0.0, 10.7, 4.0, 10.9, 4.3, 0.0, 0.0, 3.0, 3.0],
    "f": [0, 0, 0, 0, 1.3, 1.1, 1.0, 0.3, 0.7, 0.5, 1.3, 1.7, 2.1, 2.1, 2.1, 2.3, 1.7, 1.7, 2.0, 5.1, 5.4, 5.4, 5.3, 11.4, 9.0, 9.0, 9.0, 2.5, 1.6, 4.0, 4.0, 0.0, 1.6, 14.4, 3.0, 3.0, 2.7],
    "bal": [0, 0, 0, 0, 5.6, 4.3, 7.9, 1.5, 1.5, 10.5, 5.5, 11.8, 17.6, 11.6, 11.6, 12.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 11.4, 0.0, 0.0, 0.0, 0.0, 2.7, 16.0, 16.0, 0.0, 0.0, 13.1, 0.6, 0.6, 0.4]
}

# Erstellen eines DataFrames
df_mittagessen = pd.DataFrame(data_mittagessen)

# Ausgabe des DataFrames
df_mittagessen
