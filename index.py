from api.index import app

# Este archivo sirve como punto de entrada para Vercel

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0") 